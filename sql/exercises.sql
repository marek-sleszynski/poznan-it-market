//exercise 7-basic:
//simple if exercise
select name,
	case when (monthlymaintenance > 100) then
		'expensive'
	else
		'cheap'
	end as cost
	from cd.facilities;

//exercise 8-basic
//how to handle date formating
SELECT memid, surname, firstname, joindate
	FROM cd.members
	WHERE joindate >= '2012-09-01 00:00:00';

//exercise 9-basic
// how to handle duplicates, limits, ordered list ASC/DESC
SELECT DISTINCT surname
	FROM cd.members
	ORDER BY surname ASC
	LIMIT 10;

//exercise 10-basic
//how to merge columns from different databases
SELECT surname
	FROM cd.members
UNION
SELECT name
	FROM cd.facilities;

//exercise 12-basic
//how to deal with subquery-type exercise
SELECT firstname, surname, joindate
FROM cd.members
WHERE joindate = (
	SELECT MAX(joindate)
	FROM cd.members);

//exercise 3-joins and subqueries
//how to self-join 
SELECT DISTINCT m2.firstname, m2.surname
FROM cd.members m1
INNER JOIN cd.members m2
	ON m2.memid=m1.recommendedby
ORDER BY surname ASC;

//exercise 4-joins and subqueries
//how to self-join - left join 
SELECT m1.firstname, m1.surname, m2.firstname, m2.surname
FROM cd.members m1
LEFT JOIN cd.members m2
	ON m1.recommendedby=m2.memid
ORDER BY m1.surname, m1.firstname ASC;

//exercise 5-joins and subqueries
//how to self-join - 3 in a row and merging using || ' ' ||
SELECT DISTINCT m1.firstname || ' ' || m1.surname AS member, m3.name AS facility
FROM cd.members m1
INNER JOIN cd.bookings m2
    ON m1.memid = m2.memid
INNER JOIN cd.facilities m3
    ON m2.facid = m3.facid
WHERE m3.name LIKE '%Tennis Court%'
ORDER BY member, facility;

//exercise 6-joins and subqueries
//tough exercise
select mems.firstname || ' ' || mems.surname as member,
	facs.name as facility,
	case
		when mems.memid = 0 then
			bks.slots*facs.guestcost
		else
			bks.slots*facs.membercost
	end as cost
        from
                cd.members mems
                inner join cd.bookings bks
                        on mems.memid = bks.memid
                inner join cd.facilities facs
                        on bks.facid = facs.facid
        where
		bks.starttime >= '2012-09-14' and
		bks.starttime < '2012-09-15' and (
			(mems.memid = 0 and bks.slots*facs.guestcost > 30) or
			(mems.memid != 0 and bks.slots*facs.membercost > 30)
		)
order by cost desc;

//exercise 7-joins and subqueries
//method without using join 
SELECT DISTINCT m1.firstname || ' ' || m1.surname as member,
	(
	  SELECT m2.firstname || ' ' || m2.surname
	  FROM cd.members m2
	  WHERE m2.memid = m1.recommendedby
	  ) AS recommender
FROM cd.members m1
ORDER BY member

//exercise 8-joins and subqueries
//the same as exercise 6, different approach
SELECT 
    member, 
    facility, 
    cost
FROM (
    SELECT 
        mems.firstname || ' ' || mems.surname AS member,
        facs.name AS facility, 
        CASE 
            WHEN mems.memid = 0 THEN bks.slots * facs.guestcost
            ELSE bks.slots * facs.membercost
        END AS cost
    FROM cd.members mems                
    INNER JOIN cd.bookings bks 
        ON mems.memid = bks.memid
    INNER JOIN cd.facilities facs 
        ON bks.facid = facs.facid
    WHERE bks.starttime >= '2012-09-14' AND bks.starttime < '2012-09-15'
) AS booking_costs
WHERE cost > 30
ORDER BY cost DESC;
