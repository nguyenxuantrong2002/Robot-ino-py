#include <Servo.h> 
// defines pins numbers
const int stepPin =6; //clk+ 
const int dirPin = 7; //cw+ 
const int stepPin2 =8; //clk+ 
const int dirPin2 = 9; //cw+ 
const int enPin2 = 10;
const int stepPin3 =11; //clk+ 
const int dirPin3 = 12; //cw+ 
const int enPin3 = 13;
const int servo_pin4 = 4;
const int servo_pin5 = 5;
const int CB = 3;
const int Relay = 2;

Servo servo4;
Servo servo5;

  int pos4 = 90;
  int pos5 = 120;

int th1, th2, th3, th4, th5;
static bool negative = 0;



void setup() {
  Serial.begin(115200);
  
  pinMode(stepPin,OUTPUT); 
  pinMode(dirPin,OUTPUT);
  

  pinMode(stepPin2,OUTPUT); 
  pinMode(dirPin2,OUTPUT);
  pinMode(enPin2,OUTPUT);
  digitalWrite(enPin2,LOW);

  
  pinMode(stepPin3,OUTPUT); 
  pinMode(dirPin3,OUTPUT);
  pinMode(enPin3,OUTPUT);
  digitalWrite(enPin3,LOW);

  pinMode(Relay,OUTPUT);
  pinMode(CB,INPUT);

  servo4.attach(servo_pin4);
  servo5.attach(servo_pin5);

  
}
 
void control_base(int pulse,bool dir)
{
  if(dir == 1)
  {
       digitalWrite(dirPin3,LOW);//Quay Ngược chiều kim đồng hồ  
  }
  else digitalWrite(dirPin3,HIGH);//Quay Cung chiều kim đồng hồ
      for(int x = 0; x < pulse; x++) 
   {
    digitalWrite(stepPin3,HIGH);
    delayMicroseconds(400);
    digitalWrite(stepPin3,LOW);  
    delayMicroseconds(400); 
   }
}
//Dieu khien khop co 2 motor
void control_2(int pulse, int dir)
{
  if(dir == 1)
  {
    //  Quay theo chieu duong (chieu xoay nut chai)
    digitalWrite(dirPin,HIGH);
    digitalWrite(dirPin2,LOW);
  }
  else
  {
    // Quay theo chieu am
    digitalWrite(dirPin,LOW);
    digitalWrite(dirPin2,HIGH);
  }

  for(int x = 0; x < pulse; x++) {
    digitalWrite(stepPin2,HIGH);
    digitalWrite(stepPin,HIGH);
    delayMicroseconds(400);
    digitalWrite(stepPin,LOW);
    digitalWrite(stepPin2,LOW);  
    delayMicroseconds(400); 
  }
}
void control_servo(int type, int deg, bool dir)
{
  if (dir == 0)
   deg = -deg;
  if(type==0)
  {
    pos4 = pos4+deg;
    if(pos4>=170)
    {
      pos4 = 170;
    }
    else if(pos4<=0) pos4 = 0;
    servo4.write(pos4);
  }
  else if(type == 1) 
  {
    pos5 = pos5 + deg;
    if(pos5 < 20)
    {
      pos5 = 20;
    }
    else if(pos5 > 140)
    {
      pos5 = 140;
    }
    servo5.write(pos5);
  }
 
}
void control_dof(int pulse,int dir)
{
  if(dir == 0)
  {
      digitalWrite(dirPin,HIGH);//Cung chieu kim dong ho
  }
  else digitalWrite(dirPin,LOW);//Quay Ngược chiều kim đồng hồ
      for(int x = 0; x < pulse; x++) 
   {
    digitalWrite(stepPin,HIGH);
    delayMicroseconds(400);
    digitalWrite(stepPin,LOW);  
    delayMicroseconds(400); 
   }
}


void loop() {
  bool val = digitalRead(CB);
  if (val == 0)
  {
    delay(2000);
  digitalWrite(Relay,HIGH);
  delay(500);
  digitalWrite(Relay,LOW);
  }
  else digitalWrite(Relay,LOW);
  if(Serial.available())
  {   char a;
  static int v=0;
      String S = Serial.readString();
      Serial.println(S);
      Serial.println(S.length());
      for(int m = 0;m<S.length();m++)
      {
        char ch = S[m];
 
        if(S[0]=='F')
        {
          switch(ch)
          {
            case '-':
            negative = 1;
            break;
            
            case '0'...'9':
            v = v*10 + ch - '0';   // ký tự được chuyển thành số thập phân
            break;
            
            case 'A':
            control_base(v, negative);
            negative = 0;
            v = 0;
            break;
            
            case 'B':
            control_2(v,negative);
            Serial.println(v);
            negative = 0;
            v = 0;
            break;
            
            case 'C':
            control_dof(v,negative);
            negative = 0;
            v = 0;
            break;
            
            case 'D':
            control_servo(0,v,negative);
            v=0;
            negative = 0;
            break;
            
            case 'E':
            control_servo(1,v, negative);
            v=0;
            negative = 0;
            break;
          }
        }
      }
  }
}
