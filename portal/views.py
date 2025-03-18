from django.http import JsonResponse
from .models import GPSData,GPSCommand,GPSDevice
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

def parse_gps_data(request):
    if request.method == "POST":
        try:
            data = request.body.decode("utf-8").strip()
            parts = data.split(",")

            # Extracting values from the received data
            pack_len = parts[0]  # Not needed in model
            terminal_id = parts[1]
            work_no = parts[2]
            alarm_code = parts[4] if "|" in parts[4] else ""
            date_time = parts[5]

            # Convert YYMMDDHHmmss format to Django DateTimeField format
            dt_parsed = datetime.strptime(date_time, "%y%m%d%H%M%S")

            fix_flag = parts[6]
            latitude = float(parts[7])
            longitude = float(parts[8])
            speed = float(parts[9])
            course = float(parts[10])
            altitude = float(parts[11])
            odometer = float(parts[12])
            fuel_consume = float(parts[13]) if parts[13] else None
            status = parts[14]
            input_status = parts[15]
            output_status = parts[16]
            network_info = parts[17].split("|")
            mcc, mnc, lac, ci = network_info if len(network_info) == 4 else (None, None, None, None)
            battery_info = parts[18].split("|")

            # Save data to the database
            gps_data = GPSData.objects.create(
                terminal_id=terminal_id,
                work_no=work_no,
                alarm_code=alarm_code,
                date_time=dt_parsed,
                fix_flag=fix_flag,
                latitude=latitude,
                longitude=longitude,
                speed=speed,
                course=course,
                altitude=altitude,
                odometer=odometer,
                fuel_consume=fuel_consume,
                status=status,
                input_status=input_status,
                output_status=output_status,
                mcc=mcc,
                mnc=mnc,
                lac=lac,
                ci=ci,
                battery_voltage="|".join(battery_info)
            )

            return JsonResponse({"message": "GPS data saved successfully", "id": gps_data.id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def send_command(request):
    """API to send a command to a GPS tracker."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            imei = data.get("imei")
            command = data.get("command")

            device = GPSDevice.objects.filter(imei=imei).first()
            if not device:
                return JsonResponse({"error": "Device not found"}, status=404)

            GPSCommand.objects.create(device=device, command=command)
            return JsonResponse({"message": "Command added to queue"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request"}, status=400)
