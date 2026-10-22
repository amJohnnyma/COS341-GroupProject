/* begin of the non-executable code-mine for later inlining */
/* end of the non-executable code-mine */
/* begin of executable C code */
#include <stdio.h>
int main() {
int sys0;
int sys1;
int sys2;
int v1;
int v2;
v1 = 15;
v2 = 25;
sys0 = v1 + v2;
int v3;
int v4;
v3 = 50;
v4 = sys0;
sys1 = v3 - v4;
int v5;
v5 = sys1;
sys2 = -v5;
int v6;
v6 = sys2;
printf("%d\n", v6);
return 0;
}
