#include <stdarg.h>
void *__sF[3];
void android_set_abort_message(const char *s) {}
unsigned long __strlen_chk(const char *s, unsigned long n) { unsigned long i=0; while(i<n&&s[i])i++; return i; }
void *__memmove_chk(void *d,const void*s,unsigned long n,unsigned long z){return __builtin_memmove(d,s,n);}
int __vsnprintf_chk(char *d,unsigned long n,int f,unsigned long z,const char *fmt,va_list a){return __builtin_vsnprintf(d,n,fmt,a);}
int __android_log_print(int p, const char *t, const char *f, ...) { return 0; }
int __android_log_vprint(int p, const char *t, const char *f, va_list a) { return 0; }
int __android_log_write(int p, const char *t, const char *m) { return 0; }
