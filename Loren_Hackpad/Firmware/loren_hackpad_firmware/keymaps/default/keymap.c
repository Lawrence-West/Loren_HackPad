#include QMK_KEYBOARD_H
#include "raw_hid.h"
#include <string.h>

static char oled_time[9] = "00:00:00";
static char oled_date[11] = "00/00/0000";
static uint8_t oled_weather = 0;

#ifdef OLED_ENABLE
static const char* weather_icon(uint8_t code) {
    switch (code) {
        case 0: return " [SOLE]   ";
        case 1: return " [NUVOLA] ";
        case 2: return " [PIOGGIA]";
        case 3: return " [NEVE]   ";
        case 4: return " [TEMPORA]";
        case 5: return " [NEBBIA] ";
        default: return " [---]    ";
    }
}
#endif
void raw_hid_receive(uint8_t *data, uint8_t length) {
    if (data[0] == 0x01) {
        memcpy(oled_time, &data[1], 8);
        oled_time[8] = '\0';
        memcpy(oled_date, &data[9], 10);
        oled_date[10] = '\0';
        oled_weather = data[19];
    }
}

enum custom_keycodes {
    OPEN_SPOTIFY = SAFE_RANGE,
    OPEN_CHROME,
    OPEN_STEAM,
};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [0] = LAYOUT(
        KC_MPRV,       KC_MPLY,       KC_MNXT,
        KC_BRIU,       KC_BRID,       LGUI(LSFT(KC_S)),
        OPEN_SPOTIFY,  OPEN_CHROME,   OPEN_STEAM
    ),
};

#ifdef ENCODER_MAP_ENABLE
const uint16_t PROGMEM encoder_map[][NUM_ENCODERS][NUM_DIRECTIONS] = {
    [0] = { ENCODER_CCW_CW(KC_VOLD, KC_VOLU) },
};
#endif

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    if (record->event.pressed) {
        switch (keycode) {
            case OPEN_SPOTIFY:
                SEND_STRING(SS_LGUI("r"));
                wait_ms(200);
                SEND_STRING("spotify\n");
                return false;
            case OPEN_CHROME:
                SEND_STRING(SS_LGUI("r"));
                wait_ms(200);
                SEND_STRING("chrome\n");
                return false;
            case OPEN_STEAM:
                SEND_STRING(SS_LGUI("r"));
                wait_ms(200);
                SEND_STRING("steam\n");
                return false;
        }
    }
    return true;
}

#ifdef OLED_ENABLE
oled_rotation_t oled_init_user(oled_rotation_t rotation) {
    return OLED_ROTATION_0;
}

bool oled_task_user(void) {
    oled_write_P(PSTR("Ora:  "), false);
    oled_write_ln(oled_time, false);
    oled_write_P(PSTR("Data: "), false);
    oled_write_ln(oled_date, false);
    oled_write_ln(weather_icon(oled_weather), false);
    oled_write_ln_P(PSTR("Lorenzo's Hackpad"), false);
    return false;
}
#endif

#ifdef RGBLIGHT_ENABLE
void keyboard_post_init_user(void) {
    rgblight_setrgb(120, 120, 120);
}
#endif