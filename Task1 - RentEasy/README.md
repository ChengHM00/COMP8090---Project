# RentEasy - Hotel and Homestay Management System
<p align="center">
    <img src="Assets/building_hotel.png" width="400">
</p>


<center> Hong Kong Metropolitan University

Department of Electronic Engineering and Computer Science

COMP8090SEF Data Structures And Algorithms 

Final Project

Cheng Hoi Man (11666130)
</center>

----------------------------------
## Introduction

This system aim at provide solution on managing multiple resisdent renting and coresponding assets renting with simple and easy web application interface for users. The program have impliment OOP concept to improve the structure.


## Project Structure

```
.
│   
├── Assets/
├── Object/
│   ├── Facility.py
│   ├── Room.py
│   ├── Leisure.py 
├── Manager/
│   ├── CSVManager.py
│   ├── Manager.py
│   ├── ReadRecord.py
├── RentalRecord.py
├── StreamlitApp.py
├── GetManager.py
└── RentEasy.py
```

- Facility.py - Define Facility Class for all object
- Room.py - Define Room Class under Facility class for room asset
- Leisure.py - Define Leisure Class under Facility class for Leisure Facility asset

- CSVManager.py - Reocrd CSV I/O function
- ReadRecord.py - Read data dict to object
- Manager.py - Maintain Assets and Renatl Funtion

- RentalRecord.py - dataclass for represent both room and leisure rentals
- StreamlitApp.py - Streamlit Web App function 
- GetManager.py - Get Manager Function
- RentEasy.py - Main application


## Updates
- 24 Feb 2026 - Draft of this document
- 05 Apr 2026 - Main fuction ver1.0 updated
- 11 Apr 2026 - Main fuction and document updated



## Installation
```shell
git clone https://github.com/ChengHM00/COMP8090---Project.git
cd COMP8090---Project
pip install streamlit
streamlit run RentEasy.py
```
- For non-Git Environment:
- - Download the whole program
- - Open terminal in the program folder
- - install stramlit package
- - type " streamlit run RentEasy.py"
## Program Introduction Video

https://youtu.be/LdM0f9YxK_Q

## Contact
For questions about code or paper, please email HM Cheng (cheng.hm.73@gmail.com).


## Non-Commercial Use Only Declaration
The RentEasy ("Software") is made available for use, reproduction, and distribution strictly for non-commercial purposes. For the purposes of this declaration, "non-commercial" is defined as not primarily intended for or directed towards commercial advantage or monetary compensation.

By using, reproducing, or distributing the Software, you agree to abide by this restriction and not to use the Software for any commercial purposes without obtaining prior written permission from HM Cheng.

This declaration does not in any way limit the rights under any open source license that may apply to the Software; it solely adds a condition that the Software shall not be used for commercial purposes.

IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For inquiries or to obtain permission for commercial use, please contact HM Cheng (cheng.hm.73@gmail.com).