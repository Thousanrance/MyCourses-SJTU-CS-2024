/*
 * Copyright (C) 2011-2021 Intel Corporation. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   * Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in
 *     the documentation and/or other materials provided with the
 *     distribution.
 *   * Neither the name of Intel Corporation nor the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */

#include "Enclave.h"
#include "Enclave_t.h" /* print_string */
#include <stdarg.h>
#include <stdio.h> /* vsnprintf */
#include <string.h>

/* 
 * printf: 
 *   Invokes OCALL to display the enclave buffer to the terminal.
 */
int printf(const char* fmt, ...)
{
    char buf[BUFSIZ] = { '\0' };
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(buf, BUFSIZ, fmt, ap);
    va_end(ap);
    ocall_print_string(buf);
    return (int)strnlen(buf, BUFSIZ - 1) + 1;
}

#include <stdint.h>
#include <stdlib.h>

const char* key = "gosecgosec";

// S盒生成
void ecall_sbox_gen(uint8_t S[], uint8_t K[]) {
    int key_len = strlen(key);
    for (int i = 0; i < 256; i++) {
        S[i] = (uint8_t)i;
        K[i] = (uint8_t)key[i % key_len];
    }
    uint8_t j = 0;
    for (int i = 0; i < 256; i++) {
        j = (j + S[i] + K[i]) % 256;
        uint8_t tmp = S[i];
        S[i] = S[j];
        S[j] = tmp;
    }
}

// 流密钥生成
uint8_t ecall_keystream_gen(int& i, int& j, uint8_t S[]) {
    i = (i + 1) % 256;
    j = (j + S[i]) % 256;
    uint8_t tmp = S[i];
    S[i] = S[j];
    S[j] = tmp;
    int t = (S[i] + S[j]) % 256;
    return S[t];
}

// 解密函数
void ecall_rc4_dec(char* buf, size_t len, const char* ciphertext, size_t ctext_len) {
    uint8_t K[256];
    uint8_t S[256];

    // 初始化S盒
    ecall_sbox_gen(S, K);
    
    // 密文字符串每两个字符转成一个8位的二进制数
    size_t chex_size = ctext_len / 2; // 密文转化后长度，也是明文长度
    uint8_t* cipherhex = (uint8_t*)malloc(sizeof(uint8_t)*chex_size);
    char substr[2];
    for (int i = 0; i + 1 < ctext_len; i += 2) {
        substr[0] = ciphertext[i];
        substr[1] = ciphertext[i + 1];
        cipherhex[(i + 1) / 2] = strtol(substr, nullptr, 16);
    }

    // 解密
    char* plaintext = (char*)malloc(sizeof(char) * chex_size);
    for (int n = 0, i = 0, j = 0; n < chex_size; n++) {
        uint8_t keystream = ecall_keystream_gen(i, j, S); // 生成流密钥
        plaintext[n] = (char)(cipherhex[n] ^ keystream); // 分段解密
    }

    // 复制给buffer
    size_t size = len;
    if (strlen(plaintext) < len)
    {
        size = strlen(plaintext) + 1;
    }
    memcpy(buf, plaintext, size - 1);
    buf[size - 1] = '\0';
}
