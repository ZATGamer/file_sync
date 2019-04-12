import requests
import os
import csv
import json


def main():
    # TODO I will add something to combine the metadata.json files later

    # Watch the directory for changes

        # Check if changes
        # Check if printer not updated yet

    # get list of printers
    printers = get_printers()
    # if printer is not updated but doesn't exist, handle that.

    # For printer in printers do the following
    for printer in printers:
        host = printer[0]
        api = printer[1]
        if not printer_busy(host, api):
            # Generate rclone config file
            try:
                os.remove('./rclone.cfg')
            except:
                pass

            # COPY the files
            dest = "abarragree@{}:/home/abarragree/3dprinter/uploads/".format(host)
            os.system('rclone sync {} {}'.format(source, dest))

            # If printer busy, note that it was busy and needs the files once it isn't busy
        # If not busy, run rclone to sync files.


def get_printers():
    with open("./printers.csv", "r") as printer_list:
        printer_list = csv.reader(printer_list)
        printers = []
        for printer in printer_list:
            printer_info = []
            printer_info.append(printer[0]) # Host Address
            printer_info.append(printer[1]) # API Key
            printers.append(printer_info)
        return printers


def printer_busy(host, api):
    call = "http://localhost:8080/api/printer".format(host)
    s = requests.session()
    s.headers.update({'X-Api-Key': '{}'.format(api)})

    # Call the printer API and make sure it isn't printing or paused.
    response = s.get(call)
    content = json.loads(response.content)
    state = content['state']['text']
    print state
    if state != 'Printing':
        busy = 0
    else:
        busy = 1
    return busy


if __name__ == '__main__':
    not_updated = []
    source = "./files"
    main()
