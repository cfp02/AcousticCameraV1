#include <Arduino.h>
#include <driver/i2s.h>

#define SAMPLE_RATE     16000
#define BUFFER_LEN      256  // Stereo, so 256 samples = 512 values

#define I2S_BCK         GPIO_NUM_7
#define I2S_WS          GPIO_NUM_8
#define I2S_SD          GPIO_NUM_9

i2s_config_t i2s_config = {
  .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
  .sample_rate = SAMPLE_RATE,
  .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
  .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
  .communication_format = I2S_COMM_FORMAT_I2S,
  .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
  .dma_buf_count = 4,
  .dma_buf_len = 512,
  .use_apll = false,
  .tx_desc_auto_clear = false,
  .fixed_mclk = 0
};

i2s_pin_config_t pin_config = {
  .bck_io_num = I2S_BCK,
  .ws_io_num = I2S_WS,
  .data_out_num = I2S_PIN_NO_CHANGE,
  .data_in_num = I2S_SD
};

int32_t buffer[BUFFER_LEN * 2];  // 2x for stereo

void setup() {
  Serial.begin(115200);
  delay(1000);

  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);
  i2s_start(I2S_NUM_0);

  Serial.println("micL,micR");  // CSV header
}

void loop() {
  size_t bytesRead;
  i2s_read(I2S_NUM_0, &buffer, sizeof(buffer), &bytesRead, portMAX_DELAY);
  size_t samplesRead = bytesRead / sizeof(int32_t);

  for (size_t i = 0; i < samplesRead; i += 2) {
    int16_t micL = -(buffer[i] >> 14);
    int16_t micR = -(buffer[i + 1] >> 14);
    Serial.print(micL);
    Serial.print(",");
    Serial.println(micR);
  }
}