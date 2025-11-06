using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Pg121q5
{
    internal class Person
    {
        protected string id { get; set };
        protected string fName { get; set };
        protected string lName { get; set };
        protected string address { get; set };

        public Person (string id, string fName, string lName, string address)
        {
            this.id = id;
            this.fName = fName;
            this.lName = lName;
            this.address = address;
        }


    }
}
