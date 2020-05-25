/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package calculator;

/**
 *
 * @author Rupesh
 */
import java.awt.Button;
import java.awt.FlowLayout;
import java.awt.TextField;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import javax.swing.JFrame;
public class A extends JFrame implements ActionListener
{
TextField t1,t2,t3;
Button b1,b2,b3,b4,b5,b6;
public  A()
{
    setLayout(new FlowLayout());
    add(t1=new TextField(20));
    add(t2=new TextField(20));
    add(t3=new TextField(20));
    add (b1= new Button("+"));
    add (b2= new Button("*"));
    add (b3= new Button("/"));
    add (b4= new Button("-"));
    add (b5= new Button("%"));
    add (b6= new Button("EXIT"));
    b1.addActionListener(this);
    b2.addActionListener(this);
    b3.addActionListener(this);
    b4.addActionListener(this);
    b5.addActionListener(this);
    b6.addActionListener(this);
    setSize(100,300);
    setVisible(true);
}
@Override
public void actionPerformed(ActionEvent e)
{
    int a,b,c=0;
    a=Integer.parseInt(t1.getText());
    b=Integer.parseInt(t2.getText());
    if(e.getSource()==b1)
        c=a+b;
    if(e.getSource()==b2)
        c=a*b;
    if(e.getSource()==b3)
        c=a/b;
     if(e.getSource()==b4)
        c=a-b;
     if(e.getSource()==b5)
        c=a%b;
     else 
         System.exit(0);
     t3.setText(""+e);
}
}