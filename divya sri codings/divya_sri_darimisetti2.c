#include<stdio.h>
void main()
{
	int i,a,v,c,j,max;
    int count[]={0,0,0,0,0,0,0,0};
    printf("Enter no of voters:");
	scanf("%d",&v);
	for(i=1;i<=v;i++)
	{
		printf("enter voter %d castedvote:",i);
		scanf("%d",&a);	
		if(a>=1&&a<=8)
		{
		  for(j=0;j<=7;j++)
		  {
		  if(a==j+1)
		  count[j]=count[j]+1;
	      }
		  }
	    else
		{
		printf("invalid vote enter again \n");
		printf("enter voter %d castedvote:",i);
		scanf("%d",&a);
		for(j=0;j<=7;j++)
		{
		  if(a==j+1)
		  count[j]=count[j]+1;
	    }
		}
	}
	printf("\n");
	for(i=1;i<=8;i++)
	{
		
		printf("candidate %d vote count:%d",i,count[i-1]);
		printf("\n");
	}
	max=count[0];
	for(i=0;i<=7;i++)
	{
		if(max<=count[i])
		{
		max=count[i];
		c=i+1;
		}
	}
	printf("\n");
	for(i=0;i<=8;i++)
	{
		if(count[i]==max)
	printf("candidate %d is winner! \n",i+1);
	else continue ;
	}
}
