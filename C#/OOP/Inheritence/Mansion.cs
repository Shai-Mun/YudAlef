using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Inheritence
{
    internal class Mansion : PersonalProperty
    {
        private int EstimatedValue;

        public Mansion(string Owner, string Address, int Rooms, int width, int length, int height, int EstimatedValue) : base(Owner, Address, Rooms, width, length, height)
        {
            this.ParkingSpace = false;
            this.EstimatedValue = EstimatedValue;
        }

        public Mansion(string Owner, string Address) : base(Owner, Address)
        {
            this.Owner = Owner;
            this.SetAddress(Address);
            this.Type = "Mansion";
        }

        public Mansion()
        {

        }

        public override void Reminder()
        {
            if (!this.ParkingSpace)
                Console.WriteLine("Hello sir, currently you are not able to park at the designated spot.");
            else
                Console.WriteLine("Hello sir, you are able to park at your desired spot, as it is empty.");

            Console.WriteLine("Height:" + this.height);
        }

        public override void ShowMe()
        {
            Console.WriteLine("This is a Mansion");
            Console.WriteLine(string.Format("The owner is {0}, and the apartment is at {1}." +
                            "\nThe property has {2} rooms, and it's parking space status is {3}. It's volume is {4} square meters."
                            , this.Owner, this.GetAddress(), this.Rooms, this.ParkingSpace, CalcSpace(this.width, this.length, this.height)));
        }
    }
}
