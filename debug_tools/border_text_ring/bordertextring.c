#include <conio.h>
#include <stdlib.h>

#define ROWS 25
#define COLS 40

void put_random_letter(int x, int y) {
    char c;
    c = (char)('A' + (rand() % 26));
    gotoxy(x, y);
    cputc(c);
}

int main(void) {
    int x, y;

    clrscr();
    srand(1);

    for (x = 0; x < COLS; x++) {
        put_random_letter(x, 0);
        put_random_letter(x, ROWS - 1);
    }

    for (y = 1; y < ROWS - 1; y++) {
        put_random_letter(0, y);
        put_random_letter(COLS - 1, y);
    }

    while (1) {
    }

    return 0;
}
