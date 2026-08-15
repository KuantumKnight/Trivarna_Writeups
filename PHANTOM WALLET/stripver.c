#include <elf.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>
int main(int argc,char**v){int f=open(v[1],O_RDWR);struct stat s;fstat(f,&s);unsigned char*b=mmap(0,s.st_size,PROT_READ|PROT_WRITE,MAP_SHARED,f,0);Elf64_Ehdr*e=(void*)b;Elf64_Phdr*p=(void*)(b+e->e_phoff);for(int i=0;i<e->e_phnum;i++)if(p[i].p_type==PT_DYNAMIC){Elf64_Dyn*d=(void*)(b+p[i].p_offset);for(;d->d_tag;d++){if(d->d_tag==DT_VERNEED||d->d_tag==DT_VERNEEDNUM||d->d_tag==DT_VERSYM)d->d_tag=DT_NULL;}}for(size_t i=0;i+8<s.st_size;i++)if(!__builtin_memcmp(b+i,"libdl.so",8)){__builtin_memcpy(b+i,"libc.so\0",8);break;}msync(b,s.st_size,MS_SYNC);return 0;}
