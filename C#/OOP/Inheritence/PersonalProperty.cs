using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Inheritence
{
    internal class PersonalProperty : LivingSpace
    {
        protected string Type;
        protected bool ParkingSpace;
        public int Rooms;

        public PersonalProperty(string Owner, string Address, int Rooms, int width, int length, int height)
        {
            this.Owner = Owner;
            this.SetAddress(Address);
            this.ParkingSpace = false;
            this.Rooms = Rooms;
            this.width = width;
            this.length = length;
            this.height = height;
        }

        public PersonalProperty(string Owner, string Address)
        {
            this.Owner = Owner;
            this.SetAddress(Address);
        }

        public PersonalProperty()
        {

        }
        public override void ShowMe()
        {
            Console.WriteLine(string.Format("The owner is {0}, and the apartment is at {1}." +
                            "\nThe property has {2} rooms, and it's parking space status is {3}. It's volume is {4} square meters."
                            , this.Owner, this.GetAddress(),this.Rooms, this.ParkingSpace, CalcSpace(this.width, this.length, this.height)));
        }

        public void ParkCar()
        {
            this.ParkingSpace = true;
        }
        public void MoveCar()
        {
            this.ParkingSpace = false;
        }

        public virtual void Reminder()
        {
            if (!this.ParkingSpace)
            {
                Console.WriteLine("The parking space is not available, perhaps you should park somewhere else.");
            }
            else
                Console.WriteLine("The parking space is available.");
        }

        public override void PayRent()
        {
            Console.WriteLine("Since you have a personal property which is yours, you don't have to pay rent.");
        }
    }
}
