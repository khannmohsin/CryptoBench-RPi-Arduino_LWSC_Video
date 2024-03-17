#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "grain.h"


void printData(u8 *key, u8 *IV, u8 *ks) {
	u32 i;
	printf("\n\nKey:        ");
	for (i=0;i<10;++i) printf("%02x",(int)key[i]);
	printf("\nIV :        ");
	for (i=0;i<8;++i) printf("%02x",(int)IV[i]);
	printf("\nkeystream:  ");
	for (i=0;i<10;++i) printf("%02x",(int)ks[i]);
}


int hex2data(unsigned char *data, const unsigned char *hexstring, unsigned int len)
{
    unsigned const char *pos = hexstring;
    char *endptr;
    size_t count = 0;

    if ((hexstring[0] == '\0') || (strlen(hexstring) % 2)) {
        //hexstring contains no data
        //or hexstring has an odd length
        return -1;
    }

    for(count = 0; count < len; count++) {
        char buf[5] = {'0', 'x', pos[0], pos[1], 0};
        data[count] = strtol(buf, &endptr, 0);
        pos += 2 * sizeof(char);

        if (endptr[0] != '\0') {
            //non-hexadecimal character encountered
            return -1;
        };
    }

    return 0;
}
int main(int argc, char **argv) {
char str1[20];
char str2[20];    
		 
	ECRYPT_ctx ctx;

	u8 key[10] = {0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef,0x12,0x34},
		IV[8] = {0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef};
 	u8 ks[10];


   argv[1]="0123456789abcdef1234";
   argv[2]="0123456789abcdef";

	strcpy(str1, argv[1]);
	hex2data(key,  str1,10);

puts("Grain");

	strcpy(str2, argv[2]);

	hex2data(IV, str2,8);


	ECRYPT_keysetup(&ctx,key,80,64);
	ECRYPT_ivsetup(&ctx,IV);
	ECRYPT_keystream_bytes(&ctx,ks,10);
	printData(key,IV,ks);

	return 0;
}