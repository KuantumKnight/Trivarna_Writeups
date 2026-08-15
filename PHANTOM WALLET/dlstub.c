typedef int (*callback_t)(void *, void *);
extern void *dlsym(void *, const char *);
int dl_iterate_phdr(callback_t cb, void *data) { static int (*real)(callback_t,void*); if(!real) real=(int(*)(callback_t,void*))dlsym((void*)-1,"dl_iterate_phdr"); return real ? real(cb,data) : 0; }
