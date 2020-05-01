#include <Servo.h>

#define CIRCBUFFSIZE 5
#define DELAY 20
unsigned long lastRead = 0;

Servo myservo1, myservo2, myservo3, myservo4;

float th1=90.0,th2=90.0,th3=90.0,th4=90.0;
float val1, val2, val3, val4;

float th1CircBuff [CIRCBUFFSIZE];
float th2CircBuff [CIRCBUFFSIZE];
float th3CircBuff [CIRCBUFFSIZE];
float th4CircBuff [CIRCBUFFSIZE];

int circBuffIndex = 0;

float th1Ave = 0;
float th2Ave = 0;
float th3Ave = 0;
float th4Ave = 0;

void setup() {
    Serial.begin(115200);
    Serial.flush();
    attachServos(); 
    set_servo();
    lastRead = millis();
}

void loop() {
  if(millis() >= lastRead + DELAY){
    val1 = analogRead(A0); //clamp
    val2 = analogRead(A1); //base
    val3 = analogRead(A2); //hinge 1
    val4 = analogRead(A3); //hinge 2
    lastRead = millis();

    th1 = map(val1, 0.0, 1023.0, 9.0, 90.0);
    if(th1 >= 90.0){
        th1 = 90.0;
    }else if(th1 <= 9.0){
        th1 = 9.0;
    }

    th2 = map(val2, 0.0, 1023.0, 0.0, 180.0);
    if(th2 >= 180.0){
        th2 = 180.0;
    }else if(th2 <= 0.0){
        th2 = 0.0;
    }

    th3 = map(val3, 0.0, 1023.0, 0.0, 180.0);
    if(th3 >= 180.0){
        th3 = 180.0;
    }else if(th3 <= 0.0){
        th3 = 0.0;
    }

    th4 = map(val4, 0.0, 1023.0, 0.0, 180.0);
    if(th4 >= 180.0){
        th4 = 180.0;
    }else if(th4 <= 0.0){
        th4 = 0.0;
    }

    useCircBuff();
    set_servo();
    sendPots();
  }
}

void attachServos() {
    myservo1.attach(3, 700, 2300);  
    myservo2.attach(4, 700, 2300); 
    myservo3.attach(5, 700, 2300); 
    myservo4.attach(6, 700, 2300);
}

void set_servo(){
    myservo1.write(th1Ave);
    myservo2.write(th2Ave);
    myservo3.write(th3Ave);
    myservo4.write(th4Ave);
}

void useCircBuff() {
  int i=0;
  float th1Sum=0;
  float th2Sum=0;
  float th3Sum=0;
  float th4Sum=0;
  
  th1CircBuff[circBuffIndex] = th1;
  th2CircBuff[circBuffIndex] = th2;
  th3CircBuff[circBuffIndex] = th3;
  th4CircBuff[circBuffIndex] = th4;

  circBuffIndex++;
  if(circBuffIndex >= CIRCBUFFSIZE) circBuffIndex=0;
  
  for(i=0; i<CIRCBUFFSIZE; i++){
    th1Sum += th1CircBuff[i];
    th2Sum += th2CircBuff[i];
    th3Sum += th3CircBuff[i];
    th4Sum += th4CircBuff[i];
  }

  th1Ave = th1Sum / CIRCBUFFSIZE;
  th2Ave = th2Sum / CIRCBUFFSIZE;
  th3Ave = th3Sum / CIRCBUFFSIZE;
  th4Ave = th4Sum / CIRCBUFFSIZE;
  
}

void sendPots(){
  if(Serial){
    Serial.print(th1Ave);
    Serial.print(",");
    Serial.print(th2Ave);
    Serial.print(",");
    Serial.print(th3Ave);
    Serial.print(",");
    Serial.print(th4Ave);
    Serial.println(",");
  } 
}
