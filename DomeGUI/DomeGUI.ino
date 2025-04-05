#include <DHT.h>
DHT dht(A5, DHT22);

int relay_R = 12;         //реле R
int relay_L = 13;         //реле L
int relay_Open = 10;      //реле открытия купола
int relay_Close = 11;     //реле закрытия купола
int relay_0 = 8;          //реле 0 - Scop + mount
int relay_1 = 9;          //реле 1 - reserved

unsigned long curr_Time_dht;  // переменные для таймеров loop - начало цикла, curr - текущее время
unsigned long loop_Time_dht;
unsigned long curr_Time_run;  
unsigned long loop_Time_run;
unsigned long curr_Time_c;
unsigned long loop_Time_c;
unsigned long curr_Time_o;
unsigned long loop_Time_o;
float temp = 0.0;
float hum = 0;
String data_String_dht = "";
String data_String_status = "";
String data_String_az = "";

int timer_dht = 5000;    // интервал запроса температуры и влажности - не чаще 2 сек
int timer_hat = 8000;    // время открытия/закрытия купола, ms - указать для своего купола!
boolean hat_open = false;         // купол закрыт (в плане - проверить показания датчика!)
boolean hat_open_timer = false;   // реле открытия выключено
boolean hat_close_timer = false;  // реле закрытия выключено 
boolean run_on = false;           // ведение по таймеру отключено
boolean relay_0_on = false;       // питание телескопа отключено
boolean relay_1_on = false;       // реле 1 отключено
int step_time = 975;              // продолжительность шага по азимуту (975ms ~ 5 градусов)
int step_delta = 195;             // время смещения на 1 градус по азимуту, ms
float azimut_z = 0;               // текущий азимут относительно датчика 0 
unsigned long Timer_run = 200000; // период подвижек для автоведения, ms
unsigned long Day_sec = 86164;    // секунд в звездных сутках
int Turn_sec = 86;                // время полного оборота купола, сек - указать для своего купола!

void setup() {
pinMode(relay_R,OUTPUT);
pinMode(relay_L,OUTPUT); 
pinMode(relay_Open,OUTPUT);
pinMode(relay_Close,OUTPUT);
pinMode(relay_0,OUTPUT);
pinMode(relay_1,OUTPUT);

digitalWrite(relay_R,0);
digitalWrite(relay_L,0); 
digitalWrite(relay_Open,0);
digitalWrite(relay_Close,0);
digitalWrite(relay_0,0);
digitalWrite(relay_1,0);

curr_Time_dht = millis();
loop_Time_dht = curr_Time_dht;

dht.begin();
Serial.begin(9600);    // соединение и скорость передачи данных в бит/c 
}

void loop() {

curr_Time_dht = millis();
if(curr_Time_dht > loop_Time_dht + timer_dht)
{
  temp = dht.readTemperature();  // запрос температуры
  hum = dht.readHumidity();     // запрос влажности
//  Serial.print("Температура - ");
//  Serial.println(temp);
//  Serial.print("Влажность - ");
//  Serial.println(hum);
  loop_Time_dht = curr_Time_dht;
}
  if (Serial.available() > 0) // если пришли данные
  {
    char val=' ';
// S -запрос статуса купола
// s -запрос показаний датчиков
// z -запрос текущего азимута

// r -вращение вправо
// l -вращение влево
// o -открыть купол
// c -закрыть купол
// p -парковка
// 0 -питание телескопа
// 1 -питание реле №1
// A -включить ведение
// x -выключить ведение
    
    val = Serial.read();
    switch(val)
    {
    case 'r':                 // r - движение вправо
      digitalWrite(relay_R,HIGH);
      delay(step_time);
      digitalWrite(relay_R,LOW);
      azimut_z = azimut_z + (step_time / step_delta);
      if (azimut_z > 360)
      {
        azimut_z = azimut_z - 360;
      }
      break;

    case 'l':                 // l - движение влево
      digitalWrite(relay_L,HIGH);
      delay(step_time);
      digitalWrite(relay_L,LOW);
      azimut_z = azimut_z - (step_time / step_delta);
      if (azimut_z < 0)
      {
        azimut_z = azimut_z + 360;
      }
      break;
 
    case 'o':                 // o - открыть купол timer_hat секунд
       if (!hat_open)         // если купол не открыт
       {
         digitalWrite(relay_Open,HIGH);   // включение реле
         loop_Time_o = millis();          // старт таймера 
         hat_open_timer = true;           // признак "включено реле"
       }
      digitalWrite(relay_Open,LOW);
      break;

    case 'c':                 // c - закрыть купол timer_hat секунд
       if (hat_open)          // если купол открыт
       {
         digitalWrite(relay_Close,HIGH);   // включение реле
         loop_Time_c = millis();           // старт таймера 
         hat_close_timer = true;           // признак "включено реле"
       }
      digitalWrite(relay_Open,LOW);
      break;

    case '0':                 // 0 - вкл\выкл. главный
      digitalWrite(relay_0,!digitalRead(relay_0));
      relay_0_on = !relay_0_on;
      break;

    case '1':                 // 1 - вкл\выкл. реле 1
      digitalWrite(relay_1,!digitalRead(relay_1));
      relay_1_on = !relay_1_on;
      break;
      
    case 'p':                 // p - парковка
      digitalWrite(relay_R,LOW);   // выключение R и L реле
      digitalWrite(relay_L,LOW);
      run_on = false;               // признак "включено автовращение" - выкл.
      if (azimut_z < 180)
      {
        int park_time = azimut_z * step_delta;
        digitalWrite(relay_L,HIGH);
        delay(park_time);
        digitalWrite(relay_L,LOW);
        azimut_z = 0; 
      }
      else
      {
        int park_time = (360 - azimut_z) * step_delta;
        digitalWrite(relay_R,HIGH);
        delay(park_time);
        digitalWrite(relay_R,LOW);
        azimut_z = 0;  
      }
      break;

    case 'A':                 // A - звездная скорость
      digitalWrite(relay_R,HIGH);   // включение реле
      loop_Time_run = millis();     // старт таймера 
      run_on = true;                // признак "включено автовращение"
      digitalWrite(relay_R,HIGH);
      delay(Timer_run / 1000);
      digitalWrite(relay_R,LOW);
      azimut_z = azimut_z + ((Timer_run * Turn_sec / Day_sec) / step_delta);
      if (azimut_z > 360)
      {
        azimut_z = azimut_z - 360;
      }
      break;

    case 'x':                 // x - остановка ведения
      digitalWrite(relay_R,LOW);   // включение R и L реле
      digitalWrite(relay_L,LOW);
      run_on = false;               // признак "включено автовращение" - выкл.
      break;

    case 's':                 // запрос показаний датчиков
      data_String_dht = String(temp,1) + "," + String(hum,0);
      Serial.println(data_String_dht);
      break;  

    case 'S':                 // запрос статуса купола
      data_String_status = String(hat_open) + "," + String(run_on) + "," + String(relay_0_on) + "," + String(relay_1_on);
      Serial.println(data_String_status);
      break; 

    case 'z':                 // запрос азимута относительно датчика 0
      data_String_az = String(azimut_z,1);
      Serial.println(data_String_az);
      break;  

    default:
      break;
    }
  }

// проверка циклов открытия/закрытия купола и автовращения
  
    if (run_on)
  {
    curr_Time_run = millis();
    if (curr_Time_run > loop_Time_run + Timer_run)
    {
      digitalWrite(relay_R,HIGH);
      delay(Timer_run / 1000);
      digitalWrite(relay_R,LOW);
      loop_Time_run = millis();     // рестарт таймера 
      azimut_z = azimut_z + ((Timer_run / 1000) / step_delta);
      if (azimut_z > 360)
      {
        azimut_z = azimut_z - 360;
      }
    }
  }
  if (hat_open_timer)
  {
    curr_Time_o = millis();
    if (curr_Time_o > loop_Time_o + timer_hat)
    {
    digitalWrite(relay_Open,LOW);    // выключение реле
    hat_open_timer = false;          // таймер остановлен
    hat_open = true;                 // купол открыт
    }
  }
  if (hat_close_timer)
  {
    curr_Time_c = millis();
    if (curr_Time_c > loop_Time_c + timer_hat)
    {
    digitalWrite(relay_Close,LOW);   // выключение реле
    hat_close_timer = false;         // таймер остановлен
    hat_open = false;                // купол закрыт
    }
  }
}
