#include<stdio.h>
void main()
{
int i,j,n,k;
printf("Enter a number for pyramid:");
scanf("%d",&n);
for (i=0;i<=n;i++)
{
	for(j=0;j<=n-i;j++)
    {
	printf("  ");
	}
	for(k=i;k>=0;k--)
    {	
	printf(" %d",k);
	}
	for(j=1;j<=i;j++)
    {
	printf(" %d",j);
	}   
    printf ("\n");
}
}
