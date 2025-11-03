🐎 Horse Management System (Django + MySQL)
📖 Overview

This project is a Horse Management System built with Django and MySQL.
It allows two types of users — Admin and Guest — to interact with race, horse, trainer, and stable information through a simple web interface.

----------------------------------------------------------------------------
⚙️ Requirements

Before running the project, make sure you have installed the following:
- Python 3.x
- MySQL Server & Workbench
- Django
- mysqlclient

----------------------------------------------------------------------------

🧩 Installation Steps
1️⃣ Install Dependencies

Open a terminal and run:

pip install django
pip install mysqlclient

----------------------------------------------------------------------------

2️⃣ Set Up MySQL

Open MySQL Workbench and start your MySQL server.

Make sure you have a database named horse_management.
You can create it manually if needed:

CREATE DATABASE horse_management;
USE horse_management;

⚙️⚙️⚙️⚙️⚙️ Add the procedural  ⚙️⚙️⚙️⚙️⚙️

------------------------------------------------------
🧩 COPY THIS AND PASTE IN THE WORKBENCH 🧩 
------------------------------------------------------
-- create archive table once
CREATE TABLE IF NOT EXISTS old_info (
  horseId      VARCHAR(15) PRIMARY KEY,
  horseName    VARCHAR(50),
  age          INT,
  gender       VARCHAR(10),
  registration VARCHAR(50),
  stableId     VARCHAR(15)
);

DELIMITER $$

DROP PROCEDURE IF EXISTS delete_owner_and_related $$
CREATE PROCEDURE delete_owner_and_related(IN p_ownerId VARCHAR(15))
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE v_horseId VARCHAR(15);
    DECLARE remaining INT DEFAULT 0;

    -- cursor over DISTINCT horses owned by this owner
    DECLARE horse_cursor CURSOR FOR
        SELECT DISTINCT horseId
        FROM owns
        WHERE ownerId = p_ownerId;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN horse_cursor;

    read_loop: LOOP
        FETCH horse_cursor INTO v_horseId;
        IF done = 1 THEN
            LEAVE read_loop;
        END IF;

        -- 1) remove THIS owner's link to this horse
        DELETE FROM owns
        WHERE ownerId = p_ownerId
          AND horseId = v_horseId;

        -- 2) check if anyone else still owns this horse
        SELECT COUNT(*) INTO remaining
        FROM owns
        WHERE horseId = v_horseId;

        -- 3) only if NO owners remain, delete race results and the horse
        IF remaining = 0 THEN
            DELETE FROM raceresults
            WHERE horseId = v_horseId;

            -- this will fire the BEFORE DELETE trigger to archive into old_info
            DELETE FROM horse
            WHERE horseId = v_horseId;
        END IF;
    END LOOP;

    CLOSE horse_cursor;

    -- Final cleanup: delete the owner record itself
    DELETE FROM owner
    WHERE ownerId = p_ownerId;
END $$

DELIMITER ;



------------------------------------------------------
4️⃣ Create Trigger
------------------------------------------------------
DELIMITER $$

CREATE TRIGGER backup_horse_before_delete
BEFORE DELETE ON horse
FOR EACH ROW
BEGIN
    INSERT INTO old_info (
        horseId,
        horseName,
        age,
        gender,
        registration,
        stableId
    )
    VALUES (
        OLD.horseId,
        OLD.horseName,
        OLD.age,
        OLD.gender,
        OLD.registration,
        OLD.stableId
    );
END$$

DELIMITER ;


------------------------------------------------------
🧩 THATS ALL TO COPY 🧩 
------------------------------------------------------

----------------------------------------------------------------------------

3️⃣ Set Up the Project Folder

1. From the compressed project files, extract the contents.
2. Locate the folder named DML.
3. Open that folder in Visual Studio Code (VS Code).

## If you clone it from github
# then >>cd DML/DB 

----------------------------------------------------------------------------

4️⃣ Check Database Connection Settings

Open:

DB/settings.py

Scroll down to the DATABASES section and make sure it matches your MySQL setup:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'horse_management',   # Database name in MySQL
        'HOST': '127.0.0.1',          # Localhost
        'PORT': '3306',               # MySQL default port
        'USER': 'root',               # Your MySQL username
        'PASSWORD': 'password',       # Your MySQL password
    }
}


💡 Check: Change "password" to your actual MySQL root password if it’s different.
----------------------------------------------------------------------------


5️⃣ Run the Project

In the terminal inside VS Code:

cd DB
python manage.py runserver

Once the server starts, you’ll see an address like:

Starting development server at http://127.0.0.1:8000/
----------------------------------------------------------------------------
6️⃣ Access the Web App

Open your web browser and go to:

http://127.0.0.1:8000/
----------------------------------------------------------------------------

👥 Default Roles
Role	Login Method	Credentials / Notes
Admin	Login with credentials	Username: admin Password: 123
Guest	Click Browse as Guest on the home page	No login required

----------------------------------------------------------------------------

🧠 Features Summary

- Admin Functions

Add a new race and its results

Delete an owner (and related horses, results, etc.)

Move a horse to another stable

Approve a trainer to join a stable
-----------

- Guest Functions

Browse horses by owner’s last name

View trainers who trained winning horses

See total winnings per trainer

Display track statistics

🗃️ Notes

The project uses MySQL Workbench for database management.

A stored procedure and a trigger are already defined in MySQL:

delete_owner_and_related (stored procedure) (The one that u must copy)

backup_horse_before_delete (trigger to copy deleted horses into old_info) (The one that u must copy)