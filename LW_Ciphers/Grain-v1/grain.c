/*
 * REFERENCE IMPLEMENTATION OF STREAM CIPHER GRAIN VERSION 1
 *
 * Filename: grain.c
 *
 * Author:
 * Martin Hell
 * Dept. of Information Technology
 * P.O. Box 118
 * SE-221 00 Lund, Sweden,
 * email: martin@it.lth.se
 *
 * Synopsis:
 *  This file contains functions that implement the
 *  stream cipher Grain. It also implements functions 
 *  specified by the ECRYPT API.
 *
 *  NOTE: Implementation is not optimized for speed
 *  since the cipher is purely hardware oriented.
 */

#include "grain.h"

void ECRYPT_init(void){}
/*
 * Function: grain_keystream
 *
 * Synopsis
 *  Generates a new bit and updates the internal state of the cipher.
 */
u8 grain_keystream(ECRYPT_ctx* ctx) {
	u8 i,NBit,LBit,outbit;
	/* Calculate feedback and output bits */
	outbit = N(79)^N(78)^N(76)^N(70)^N(49)^N(37)^N(24)^boolTable[(X4<<4) | (X3<<3) | (X2<<2) | (X1<<1) | X0];
	NBit=L(80)^N(18)^N(66)^N(80)^NFTable[(N(17)<<9) | (N(20)<<8) | (N(28)<<7) | (N(35)<<6) | (N(43)<<5) | (N(47)<<4) | (N(52)<<3) | (N(59)<<2) | (N(65)<<1) | N(71)];
	LBit=L(18)^L(29)^L(42)^L(57)^L(67)^L(80);
	/* Update registers */
	for (i=1;i<(ctx->keysize);++i) {
		ctx->NFSR[i-1]=ctx->NFSR[i];
		ctx->LFSR[i-1]=ctx->LFSR[i];
	}
	ctx->NFSR[(ctx->keysize)-1]=NBit;
	ctx->LFSR[(ctx->keysize)-1]=LBit;
	return outbit;
}


/* Functions for the ECRYPT API */

void ECRYPT_keysetup(
  ECRYPT_ctx* ctx, 
  const u8* key, 
  u32 keysize,                /* Key size in bits. */ 
  u32 ivsize)				  /* IV size in bits. */ 
{
	ctx->p_key=key;
	ctx->keysize=keysize;
	ctx->ivsize=ivsize;
}

/*
 * Function: ECRYPT_ivsetup
 *
 * Synopsis
 *  Load the key and perform initial clockings.
 *
 * Assumptions
 *  The key is 10 bytes and the IV is 8 bytes. The
 *  registers are loaded in the following way:
 *  
 *  NFSR[0] = lsb of key[0]
 *  ...
 *  NFSR[7] = msb of key[0]
 *  ...
 *  ...
 *  NFSR[72] = lsb of key[9]
 *  ...
 *  NFSR[79] = msb of key[9]
 *  LFSR[0] = lsb of IV[0]
 *  ...
 *  LFSR[7] = msb of IV[0]
 *  ...
 *  ...
 *  LFSR[56] = lsb of IV[7]
 *  ...
 *  LFSR[63] = msb of IV[7]
 */
void ECRYPT_ivsetup(
  ECRYPT_ctx* ctx, 
  const u8* iv)
{
	u32 i,j;
	u8 outbit;
	/* load registers */
	for (i=0;i<(ctx->ivsize)/8;++i) {
		for (j=0;j<8;++j) {
			ctx->NFSR[i*8+j]=((ctx->p_key[i]>>j)&1);  
			ctx->LFSR[i*8+j]=((iv[i]>>j)&1);
		}
	}
	for (i=(ctx->ivsize)/8;i<(ctx->keysize)/8;++i) {
		for (j=0;j<8;++j) {
			ctx->NFSR[i*8+j]=((ctx->p_key[i]>>j)&1);
			ctx->LFSR[i*8+j]=1;
		}
	}
	/* do initial clockings */
	for (i=0;i<INITCLOCKS;++i) {
		outbit=grain_keystream(ctx);
		ctx->LFSR[79]^=outbit;
		ctx->NFSR[79]^=outbit;             
	}
}

/*
 * Function: ECRYPT_keystream_bytes
 *
 * Synopsis
 *  Generate keystream in bytes.
 *
 * Assumptions
 *  Bits are generated in order z0,z1,z2,...
 *  The bits are stored in a byte in order:
 *  
 *  lsb of keystream[0] = z0
 *  ...
 *  msb of keystream[0] = z7
 *  ...
 *  lsb of keystream[1] = z8
 *  ...
 *  msb of keystream[1] = z15
 *  ...
 *  ...
 *  ...
 *  Example: The bit keystream: 10011100 10110011 ..
 *  corresponds to the byte keystream: 39 cd ..
 */
void ECRYPT_keystream_bytes(
  ECRYPT_ctx* ctx, 
  u8* keystream, 
  u32 msglen)
{
	u32 i,j;
	for (i = 0; i < msglen; ++i) {
		keystream[i]=0;
		for (j = 0; j < 8; ++j) {
			keystream[i]|=(grain_keystream(ctx)<<j);
		}
	}
}
void ECRYPT_encrypt_bytes(
  ECRYPT_ctx* ctx, 
  const u8* plaintext, 
  u8* ciphertext, 
  u32 msglen)
{
	u32 i,j;
	u8 k;
	for (i = 0; i < msglen; ++i) {
		k=0;
		for (j = 0; j < 8; ++j) {	
			k|=(grain_keystream(ctx)<<j);
		}
		ciphertext[i]=plaintext[i]^k;
	}
}

void ECRYPT_decrypt_bytes(
  ECRYPT_ctx* ctx, 
  const u8* ciphertext, 
  u8* plaintext, 
  u32 msglen)
{
	u32 i,j;
	u8 k=0;
	for (i = 0; i < msglen; ++i) {
		k=0;
		for (j = 0; j < 8; ++j) {
			k|=(grain_keystream(ctx)<<j);
		}
		plaintext[i]=ciphertext[i]^k;
	}
}