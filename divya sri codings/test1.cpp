#include <stdio.h>

int main(){
    int n;
    printf("enter n0");
    scanf("%d",&n);
    int p=1,i,a[n];
    for(i=0;i<n;i++)
    {
        scanf("%d",&a[i]);
    }
    for(i=0;i<n;i++)
    {
        p*=a[i];
    }
    printf("%d",p);
    return p;
}

