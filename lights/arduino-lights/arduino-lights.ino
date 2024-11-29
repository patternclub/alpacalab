#include <DmxMaster.h>

void setup() {
  Serial.begin(115200);
  Serial.println("SerialToDmx ready\r\n");
}

int value = 0;
int channel = 0;
int channels_per_light = 4;

void loop() {
  int c;

  while(!Serial.available());
  c = Serial.read();
  if ((c >= '0') && (c <= '9')) {
    value = 10*value + c - '0';
  }
  else {
    if (c == 'c') {
      channel = value * channels_per_light;
    }
    else if (c=='l') {
      DmxMaster.write(1+channel, value);
    }
    else if (c=='r') {
      DmxMaster.write(2+channel, value);
    }
    else if (c=='g') {
      DmxMaster.write(3+channel, value);
    }
    else if (c=='b') {
      DmxMaster.write(4+channel, value);
    }

    // 6 channel strobe
    else if (c=='S') {
      // strobe style
      DmxMaster.write(2+channel, value);
    }
    else if (c=='D') {
      // strobe duration
      DmxMaster.write(3+channel, value);
    }
    else if (c=='R') {
      DmxMaster.write(4+channel, value);
    }
    else if (c=='G') {
      DmxMaster.write(5+channel, value);
    }
    else if (c=='B') {
      DmxMaster.write(6+channel, value);
    }
    
    else if (c=='x') {
      for (int i = 0; i < 9; ++i) {
        DmxMaster.write(i+1, 0);
      }
      //Serial.println("panic over");
    }    
    value = 0;
  }
}
