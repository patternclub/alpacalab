#include <DmxMaster.h>

void setup() {
  Serial.begin(115200);
  //Serial.println("SerialToDmx ready");
}

int value = 0;
int channel = 0;

void loop() {
  int c;

  while(!Serial.available());
  c = Serial.read();
  if ((c >= '0') && (c <= '9')) {
    value = 10*value + c - '0';
  }
  else {
    if (c=='x') {
      channel = 0;
    }
    else if (c == 'y') {
      channel = 3;
    }
    else if (c == 'z') {
      channel = 6;
    }
    else if (c=='r') {
      DmxMaster.write(1+channel, value);
    }
    else if (c=='g') {
      DmxMaster.write(2+channel, value);
    }
    else if (c=='b') {
      DmxMaster.write(3+channel, value);
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
