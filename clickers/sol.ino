
// (c) Alex McLean 2023 
// Shared under terms of GPLv3 or later

#define MAXSZ 128

#define VERBOSITY 0

#define MAX_ARGS 8

const int pincount = 16;
const int pins[pincount] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};

int activation[pincount] = {-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1};
int deactivation[pincount] = {-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1};

// amount of time to use full power to move the solenoid (vs hold it)
const int millis_fire = 250;

// once fired and in 'hold' mode, switch on once in every 'n' cycles (to save power)
const int hold_ratio = 2;

const int fire_power = 255;
const int hold_power = 200;

void setup() {
  // put your setup code here, to run once:
  for(int i=0; i<pincount; ++i) {
    pinMode(pins[i], OUTPUT);// set pin as output
    digitalWrite(pins[i], LOW); 
  }
  Serial.begin(115200);
  if (VERBOSITY >= 1) {
    Serial.print("---\nABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvywxyz0123456789\n---\nHello.\n");
  }
}

void parse_command(char *cmd) {
  if (cmd[0] == '\0') {
    return;
  }

  int args[MAX_ARGS];
  char *argp = cmd;

  // parse some ints
  int eol = 0;
  for (int argi = 0; argi < MAX_ARGS; ++argi) {
    if (eol) {
      args[argi] = 0;
    }
    else {   
      args[argi] = atoi(argp);    
      while(*argp != ':') {
        if (*argp == '\0') {
          eol = 1;
          break;
        }
        argp++;
      }
      argp++;
    }
  }
  
  int pin = args[0]; // default pin 0
  int dur = args[1] ? args[1] : 250; // default 1/4 second
  int del = args[2]; // default zero delay

  if (VERBOSITY > 1) {
    char buf[128];
    snprintf(buf, 128, "pin %d dur %d del %d", pin, dur, del);
    Serial.println(buf);
  }

  if (pin < pincount) {
    activation[pin] = millis() + del;
    deactivation[pin] = millis() + dur + del;
    if (VERBOSITY > 1) {
      Serial.print("Now: ");
      Serial.print(millis());
      Serial.print(" Activation: ");
      Serial.print(activation[pin]);
      Serial.print(" Deactivation: ");
      Serial.println(deactivation[pin]);
    }
  }
}

void loop() {
  int timenow = millis();
  static char incoming[MAXSZ];
  static int incoming_n = 0;
  static int loops = 0;

  // test mode..
  //if ((millis() % 2000) > 1000) {
  //    for (int i=0; i < pincount; ++i) {
  //      analogWrite(pins[i], 255);
  //    }
  //}
  //else {
  //    for (int i=0; i < pincount; ++i) {
  //      analogWrite(pins[i], 0);
  //    }
  //}
  //
  //return;

  // put your main code here, to run repeatedly:
  for (int i=0; i < pincount; ++i) {
    int power = 0;
    if (activation[i] <= timenow && deactivation[i] > timenow) {
      if((timenow - activation[i]) < millis_fire) {
        power = fire_power;
      }
      else {
        power = hold_power;
      }
    }
    analogWrite(pins[i], power);
  }
  
  while(Serial.available()) {
    int c = Serial.read();
    if (c == '\n' || c == '\r') {
      incoming[incoming_n] = '\0';
      if (VERBOSITY >= 2) {
        Serial.print("received: ");
        Serial.println(incoming);
      }
      parse_command(incoming);
      incoming_n = 0;
    }
    else if (incoming_n < MAXSZ) {
      incoming[incoming_n] = c;
      ++incoming_n;
    }
  }
  ++loops;
}
