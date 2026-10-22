/* begin of the non-executable code-mine for later inlining */
/* end of the non-executable code-mine */
/* begin of executable C code */
#include <stdio.h>
int main() {
int sys0;
sys0 = 3;
L1:
int v1;
v1 = sys0;
printf("%d\n", v1);
int v2;
int v3;
v2 = sys0;
v3 = 1;
sys0 = v2 - v3;
int v4;
int v5;
v4 = sys0;
v5 = 0;
if (v4 == v5) goto L1;
L3:
return 0;
}
