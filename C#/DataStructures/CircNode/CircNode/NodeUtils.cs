using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CircNode
{
    class NodeUtils
    {

        // {5,2,9,-2}
        public static Node<T> BuildChainFromArray<T>(T[] a)
        {
            Node<T> head = new Node<T>(a[0]);
            Node<T> p = head;

            for (int i = 1; i < a.Length; i++)
            {
                Node<T> n1 = new Node<T>(a[i]);
                p.SetNext(n1);
                p = n1; // p = p.GetNext();
            }
            return head;
        }

        public static Node<T> BuildChainFromArray2<T>(T[] a)
        {
            Node<T> head = null;
            for (int i = a.Length -1 ; i >= 0; i--)
                 head = new Node<T>(a[i], head);
            return head;
        }


        public static int Sum (Node<int> lst)
        {
            Console.WriteLine("1----");
            Console.WriteLine(lst);
            int sum = 0;
            while(lst != null)
            {
                sum += lst.GetValue();
                lst = lst.GetNext();
            }
            
            Console.WriteLine(lst);
            Console.WriteLine("2----");
            return sum;
        }

        public static Node<int> DeleteFirst(Node<int> lst)
        {
            Console.WriteLine("3----");
            Console.WriteLine(lst);
            lst = lst.GetNext();
            
            Console.WriteLine("4----");
            Console.WriteLine(lst);

            return lst;
        }


    }
}
