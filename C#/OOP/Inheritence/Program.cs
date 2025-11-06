using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Inheritence
{
    internal class Program
    {
        static void Main(string[] args)
        {

            Apartment a = new Apartment("Shai Muntner", "Zelivansky 10", 5, 16, 10, 10, 2, 6);
            a.UnlockDoor();
            a.Reminder();
            a.LockDoor();
            a.ShowMe();
            a.PayRent();

            Console.WriteLine();

            PersonalProperty p = new PersonalProperty("Shai Muntner", "Zelivansky 10", 7, 10, 10, 2);
            p.Reminder();
            p.ParkCar();
            p.Reminder();
            p.ShowMe();
            p.PayRent();

            Console.WriteLine();

            Mansion m = new Mansion("Shai Muntner", "Zelivansky 10", 7, 10, 10, 2, 1000000);
            Mansion m2 = new Mansion();

        }
    }
}
