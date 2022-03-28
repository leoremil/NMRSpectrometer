#define TRANSMIT_PIN 11
#define RECEIVE_PIN 10
#define OSCILLOSCOPE_TRIGGER 9
#define TRANSMIT_TRIGGER 12

int serial_control = 1;

double expulse_freq_arr[] = {290};
double expulse_duration_arr[] = {200e-6};

const int num_freq_arr_elements = sizeof(expulse_freq_arr)/sizeof(expulse_freq_arr[0]);
const int num_duration_arr_elements = sizeof(expulse_duration_arr)/sizeof(expulse_duration_arr[0]);


void setup() 
{

	Serial.begin(19200);

	pinMode(LED_BUILTIN, OUTPUT);
	digitalWrite(LED_BUILTIN, LOW);

	pinMode(TRANSMIT_PIN, OUTPUT);
	digitalWrite(TRANSMIT_PIN, LOW);

	pinMode(RECEIVE_PIN, OUTPUT);
	digitalWrite(RECEIVE_PIN, LOW);	

	pinMode(OSCILLOSCOPE_TRIGGER, OUTPUT);
	digitalWrite(OSCILLOSCOPE_TRIGGER, LOW);	

	pinMode(TRANSMIT_TRIGGER, OUTPUT);
	digitalWrite(TRANSMIT_TRIGGER, LOW);	

	delay(1000);

}

void loop() 
{

	if (Serial.available() > 0) 
	{
		serial_control = Serial.parseInt();
	}

	// Send integer 1 to device over serial to start sequence
	if (serial_control == 1)
	{

		for (int i = 0; i < num_freq_arr_elements; i++)
		{
			for (int j = 0; j < num_duration_arr_elements; j++)
			{

				Serial.print(i);
				Serial.print(" ");
				Serial.println(j);

				// for (int h = 0; h < 10; h++)
				// {
				Pulse(expulse_freq_arr[i], int(expulse_duration_arr[j]/1e-6), 500);

					// for (int i = 0; i < 85; i++)
					// {
					// 	Pulse(length*2, freq, 5000);
					// }

					// for (int i = 0; i < 85; i++)
					// {
					// 	Pulse(length*2, freq+10, 5000);
					// }

					// delay(20000);
				// }
			}
		}
		serial_control = 0;
	}

	digitalWrite(LED_BUILTIN, HIGH);
	delay(500);
	digitalWrite(LED_BUILTIN, LOW);
	delay(500);

}

void Pulse(int freq, int length, int sample_time)
{


	// Initialize PWM timer
	TCCR1A &= ~7;
	TCCR1B &= ~7;

	// Enable transmit relay and wait for relay to stabilize
	digitalWrite(TRANSMIT_PIN, HIGH);
	delayMicroseconds(200);

	// Generate transmit pulse

	TCCR1A = (1 << COM1B1) | (1 << COM1B0) | (1 << WGM11);
	TCCR1B = (1 << WGM13) | (1 << WGM12);
	ICR1 = freq;
	OCR1B = freq/2; 
	TCCR1B |= (1 << CS10);

	delayMicroseconds(length); 
	digitalWrite(TRANSMIT_TRIGGER, LOW);

	// Wait for RF coil voltage to ringdown before turning of transmit relay
	delayMicroseconds(100);
	digitalWrite(TRANSMIT_PIN, LOW);

	// Small delay before enabling receive relay
	delayMicroseconds(100); 
	digitalWrite(RECEIVE_PIN, HIGH);
	digitalWrite(OSCILLOSCOPE_TRIGGER, HIGH);

	// Wait sample time before turning of receive pin
	delay(sample_time);
	digitalWrite(RECEIVE_PIN, LOW);
	digitalWrite(OSCILLOSCOPE_TRIGGER, LOW);

}