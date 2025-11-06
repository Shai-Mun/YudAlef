using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace Pg121q5
{
    internal class Employer : Person
    {
        protected string division { get; set };

        public Employer(string id, string fName, string lName, string address, string division) : base(id, fName, lName, address)
        {
            this.division = division;
        }

        
    }
}
