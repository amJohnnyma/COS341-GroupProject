/* begin of the non-executable code-mine for later inlining */
/* end of the non-executable code-mine */
/* begin of executable C code */
#include <stdio.h>
int main() {
int sys0;
sys0 = 5;
L1:
int v1;
int v2;
v1 = sys0;
v2 = 0;
if (v1 > v2) goto L2;
goto L3;
L2:
/* if */
int v3;
int v4;
v3 = sys0;
v4 = 3;
if (v3 == v4) goto L4;
L5: /* else */
goto L6;
L4: /* then */
int v5;
v5 = sys0;
printf("%d\n", v5);
L6: /* continue */
int v6;
int v7;
v6 = sys0;
v7 = 1;
sys0 = v6 - v7;
goto L1;
L3:
return 0;
}
