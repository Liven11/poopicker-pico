# PS5 Server Pico

<br>

This is a project designed for the <a href=https://www.raspberrypi.com/products/raspberry-pi-pico/>Raspberry Pi Pico W</a> board to provide a wifi http(s) server, dns server.

it is for the <a href=https://github.com/Cryptogenic/PS5-IPV6-Kernel-Exploit>PS5 3.xx / 4.xx Kernel Exploit</a>.

using this fork of the exploit <a href=https://github.com/idlesauce/PS5-Exploit-Host>PS5 3.xx / 4.xx Kernel Exploit</a> by idlesauce.

<br>

you can access the main page from the userguide.<br>

<br> 




## Libraries



install or update the <a href=https://github.com/earlephilhower/arduino-pico>pico core</a> by adding this url to the <a href=https://docs.arduino.cc/learn/starting-guide/cores>Additional Boards Manager URLs</a> section in the arduino "<b>Preferences</b>".

` https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json `

then goto the "<b>Boards Manager</b> and install or update the "<b>Raspberry PI Pico/RP2040</b>" core.<br>


Tom's Hardware presented a very nice writeup on installing arduino-pico on both Windows and Linux, available at https://www.tomshardware.com/how-to/program-raspberry-pi-pico-with-arduino-ide

<br>


## Uploading to board

installation is simple you just use the arduino ide to flash the sketch/firmware to the pico board with the following board settings.<br>


<img src=https://github.com/stooged/PS5-Server-Pico/blob/main/images/board.jpg><br>


<br>

alternatively you can download the <a href=https://github.com/stooged/PS5-Server-Pico/releases>PS5_Server_Pico.uf2</a> file then connect your pico to your pc and drop the file into the storage drive the pico creates, the board will update and reboot.<br>



 
<br>
next you connect to the wifi access point with a pc/laptop, <b>PS5_WEB_AP</b> is the default SSID and <b>password</b> is the default password.<br>
then use a webbrowser and goto http://10.1.1.1/admin.html <b>10.1.1.1</b> is the defult webserver ip or http://ps5.local<br>
on the side menu of the admin page select <b>File Uploader</b> and then click <b>Select Files</b> and locate the files and click <b>Upload Files</b>
you can then goto <b>Config Editor</b> and change the password for the wifi ap.

<br>



## Internal pages

* <b>admin.html</b> - the main landing page for administration.

* <b>info.html</b> - provides information about the pico board.

* <b>upload.html</b> - used to upload files(<b>.bin</b>) to the pico board for the webserver.

* <b>fileman.html</b> - used to <b>view</b> / <b>download</b> / <b>delete</b> files on the internal storage of the pico board.

* <b>config.html</b> - used to configure wifi ap and ip settings.

* <b>format.html</b> - used to format the internal storage of the pico board.

* <b>reboot.html</b> - used to reboot the pico board


<br><br>



## Cases

i have created a basic printable case for the pico w.<br>
the case can be printed in PLA without supports.

<a href=https://github.com/stooged/PS5-Server-Pico/tree/main/3D_Printed_Cases/PicoW>PICO-W</a><br>

<br>

if you wish to edit the case you can import the `.stl` files into <a href=https://www.tinkercad.com/>Tinkercad<a/> and edit them to suit your needs.

<br>