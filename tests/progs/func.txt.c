/* begin of the non-executable code-mine for later inlining */
/* end of the non-executable code-mine */
/* begin of executable C code */
#include <stdio.h>
int main() {
int sys0;
int f3_sys2;
int f3_v1;
int f3_v2;
int f3_v3;
int v5;
v5 = 6;
f3_sys2 = v5;
f3_v2 = f3_sys2;
f3_v3 = f3_sys2;
f3_v1 = f3_v2 * f3_v3;
sys0 = f3_v1;
int v6;
v6 = sys0;
printf("%d\n", v6);
return 0;
}
