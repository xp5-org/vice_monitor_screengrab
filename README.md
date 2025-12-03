# pygame vice remote monitor screen capture tool

uses the vice remote monitor (telnet style) port 6510 to 

- check memory of vice & C64
- copy active sprites
- save screen color & character data
- load ROM or ram character set

it does not work for bitmaps at this time, only character text graphics


<div style="display:flex; gap:6px;">
  <img src="https://github.com/user-attachments/assets/d7ef1427-386b-4f41-8594-bdde5d78db02" style="width:55%;">
  <img src="https://github.com/user-attachments/assets/57ce2580-b8c6-45a7-9300-b65c2affdef0" style="width:44%;">
</div>



<img width="2154" height="801" alt="image" src="https://github.com/user-attachments/assets/6dbe8283-728c-4076-811e-c847ed48def5" />


## output to C char array

example using 1983 seasons greetings christmas demo

<img width="1146" height="823" alt="image" src="https://github.com/user-attachments/assets/d7ef1427-386b-4f41-8594-bdde5d78db02" />

when saivng, it makes a <name>.out_char.txt file
<div style="display:flex; gap:6px;">
<img alt="image" src="https://github.com/user-attachments/assets/309d8561-79bd-4910-b82c-b59a083c8955" style="width:49%";>
<img alt="image" src="https://github.com/user-attachments/assets/7d86594e-7b28-4060-af16-cabed5c12cbc" style="width:49%;">
</div>

put the char arrays into CC65 on 8bitworkshop , copy into the vic bank and after some setup will have a copy of the demo's petscii graphics
<img width="1221" height="701" alt="image" src="https://github.com/user-attachments/assets/107889a2-05c3-43ac-a16e-3e73bf221ba4" />
