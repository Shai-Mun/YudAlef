using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Inheritence
{
    internal class Apartment : LivingSpace
    {
        private int Floor;
        private int ApartNum;
        protected int ApartTenants;
        private bool Locked;

        public Apartment(string Owner, string Address, int Floor, int ApartNum, int width, int length, int height, int Tenants)
        {
            this.Owner = Owner;
            this.SetAddress(Address);
            this.Floor = Floor;
            this.ApartNum = ApartNum;
            this.width = width;
            this.length = length;
            this.height = height;
            this.ApartTenants = Tenants;
        }

        public Apartment(string Owner, string Address)
        {
            this.Owner = Owner;
            this.SetAddress(Address);
        }

        public void LockDoor()
        {
            this.Locked = true;
        }
        public void UnlockDoor()
        {
            this.Locked = false;
        }

        public override void ShowMe()
        {
            Console.WriteLine(string.Format("The owner is {0}, and the apartment is at {1}." +
                "\nThe apartment's number is {2}, and it's located on floor {3}. It's volume is {4} square meters. In the apartment there are {5} tenants."
                ,this.Owner, this.GetAddress(), this.ApartNum, this.Floor, CalcSpace(this.width, this.length, this.height), this.ApartTenants));

        }

        public override void PayRent()
        {
            Console.WriteLine("Since you live in an apartment, you need to pay rent every month");
        }

        public virtual void Reminder()
        {
            if (!this.Locked)
            {
                Console.WriteLine("Howdy there! Lock your door before you go out!");
            }
        }
    }
}
