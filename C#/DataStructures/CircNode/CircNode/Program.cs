using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CircNode
{
    internal class Program
    {
        static void Main(string[] args)
        {
            int[] arr = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 };
            Node<int> lst = NodeUtils.BuildChainFromArray(arr);


            MakeCircular(lst, 6);
            Console.WriteLine(IsCircular(lst));
            if (CirclePoint(lst) != null)
                Console.WriteLine(CirclePoint(lst).GetValue());
            Console.WriteLine(Length(lst));
            PrintNode(lst);

            DisconnectCircle(lst);

            Console.WriteLine(IsCircular(lst));
            if (CirclePoint(lst) != null)
                Console.WriteLine(CirclePoint(lst).GetValue());
            Console.WriteLine(Length(lst));
            PrintNode(lst);
        }

        public static void MakeCircular<T>(Node<T> lst, int n)
        {
            Node<T> p = lst;
            int cnt = 0;
            Node<T> connection = null;
            while (p.GetNext() != null)
            {
                if (cnt == n)
                    connection = p;
                cnt++;
                p = p.GetNext();
            }
            p.SetNext(connection);

        }

        public static bool IsCircular<T>(Node<T> lst)
        {
            Node<T> pSlow = lst;
            Node<T> pFast = lst.GetNext();

            if (pFast == null)
                return false;

            while (pFast.GetNext() != null && pFast.GetNext().GetNext() != null)
            {
                if (pSlow == pFast)
                    return true;
                pSlow = pSlow.GetNext();
                pFast = pFast.GetNext().GetNext();
            }

            return false;
        }

        public static Node<T> CirclePoint<T>(Node<T> lst)
        {
            if (!IsCircular(lst))
                return null;

            Node<T> pSlow = lst;
            Node<T> pFast = lst;

            bool first = true;
            while (pSlow != pFast || first)
            {
                pSlow = pSlow.GetNext();
                pFast = pFast.GetNext().GetNext();
                first = false;
            }

            pSlow = lst;
            while (pSlow != pFast)
            {
                pSlow = pSlow.GetNext();
                pFast = pFast.GetNext();
            }

            return pSlow;
        }

        public static int Length<T>(Node<T> lst)
        {
            Node<T> tmp = lst;
            int cnt = 0;

            if (!IsCircular(lst))
            {
                while (tmp != null)
                {
                    cnt++;
                    tmp = tmp.GetNext();
                }
            }
            else
            {
                Node<T> Circle = CirclePoint(lst);
                while (tmp != Circle)
                {
                    cnt++;
                    tmp = tmp.GetNext();
                }
                cnt++;
                tmp = tmp.GetNext();
                while (tmp != Circle)
                {
                    cnt++;
                    tmp = tmp.GetNext();
                }
            }
            return cnt;
        }

        public static void PrintNode<T>(Node<T> lst)
        {
            Node<T> tmp = lst;

            if (!IsCircular(lst))
            {
                while (tmp.GetNext().GetNext() != null)
                {
                    Console.Write(tmp.GetValue() + "->");
                    tmp = tmp.GetNext();
                }
                Console.Write(tmp.GetNext().GetValue()+"\n");
            }
            else
            {
                Node<T> Circle = CirclePoint(lst);
                
                while (tmp != Circle)
                {
                    Console.Write(tmp.GetValue() + "->");
                    tmp = tmp.GetNext();
                }
                Console.Write("(");
                while (tmp.GetNext() != Circle)
                {
                    Console.Write(tmp.GetValue() + "->");
                    tmp = tmp.GetNext();
                }
                Console.Write(tmp.GetValue() + ")\n");
            }
        }

        public static void DisconnectCircle<T>(Node<T> lst)
        {
            if (!IsCircular(lst))
                return;

            Node<T> Circle = CirclePoint(lst);
            Node<T> tmp = Circle;

            while (tmp.GetNext() != Circle)
            {
                tmp = tmp.GetNext();
            }
            tmp.SetNext(null);

        }
    }
}
