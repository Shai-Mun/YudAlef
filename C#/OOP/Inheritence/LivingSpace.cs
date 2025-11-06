using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Inheritence
{
    abstract class LivingSpace
    {
        public string Owner { get; set; }
        private string Address;
        protected int width;
        protected int length;
        protected int height;

        public void SetAddress(string Address)
        {
            this.Address = Address;
        }
        public string GetAddress()
        {
            return this.Address;
        }
        public int CalcSpace(int width, int length, int height)
        {
            return width * height * length;
        }

        abstract public void ShowMe();
        abstract public void PayRent();
    }
}
