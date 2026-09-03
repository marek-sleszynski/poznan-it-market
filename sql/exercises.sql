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
ORDER BY cost DESC

//exercise 6-Aggregates
//how to extract month and year, multiple grouping 

select facid, extract(month from starttime) as month, sum(slots) as "Total Slots"
	from cd.bookings
	where extract(year from starttime) = 2012
	group by facid, month
order by facid, month;

//exercise 8-Aggregates
//having (aggregates) and proper order from->where->group by->having->select->order by
select facid, sum(slots) as "Total Slots"
        from cd.bookings
        group by facid
        having sum(slots) > 1000
        order by facid

//exercise 9-Aggregates
//though exercise
select facs.name, sum(slots * case
			when memid = 0 then facs.guestcost
			else facs.membercost
		end) as revenue
	from cd.bookings bks
	inner join cd.facilities facs
		on bks.facid = facs.facid
	group by facs.name
order by revenue;

//exercise 10-Aggregates
//though exercise with nested code
SELECT name, revenue
FROM (
    SELECT fac.name, sum(slots * case
                     when memid=0 then fac.guestcost
                     else fac.membercost
                     end) as revenue
    FROM cd.bookings book
    INNER JOIN cd.facilities fac
        ON fac.facid=book.facid
    GROUP BY fac.name
) as booking_revenues
WHERE revenue > 1000
ORDER BY revenue;

//exercise 12-Aggregates
//rollup (shows all months per facility and a total for all months for all facilities)
select facid, extract(month from starttime) as month, sum(slots) as slots
	from cd.bookings
	where
		starttime >= '2012-01-01'
		and starttime < '2013-01-01'
	group by rollup(facid, month)
order by facid, month;

//exercise 13-Aggregates
//shows how to use trim 
select facs.facid, facs.name,
	trim(to_char(sum(bks.slots)/2.0, '9999999999999999D99')) as "Total Hours"

	from cd.bookings bks
	inner join cd.facilities facs
		on facs.facid = bks.facid
	group by facs.facid, facs.name
order by facs.facid;

//exercise 13-Aggregates
//first booking/ interesting exercise
select mems.surname, mems.firstname, mems.memid, min(bks.starttime) as starttime
	from cd.bookings bks
	inner join cd.members mems on
		mems.memid = bks.memid
	where starttime >= '2012-09-01'
	group by mems.surname, mems.firstname, mems.memid
order by mems.memid;

//exercise 14-Aggregates
//how to use over()- without crashing a row
select count(*) over(), firstname, surname
from cd.members
order by joindate

//exercise 15-Aggregates
//how to use over()- extended
select row_number() over(order by joindate), firstname, surname
from cd.members
order by joindate;

//exercise 16-Aggregates
//how to print highest (2 prints in a draw )
WITH suma_slotow AS (
    SELECT facid, sum(slots) AS total
    FROM cd.bookings
    GROUP BY facid
)
SELECT facid, total
FROM suma_slotow
WHERE total = (
    SELECT MAX(total) FROM suma_slotow
);

//exercise 19-Aggregates
//internesting exercise with rank() and over()
WITH ranking_obiektow AS (
    SELECT fac.name,
           rank() over(order by sum(book.slots * case
                                    when book.memid=0 then fac.guestcost
                                    else fac.membercost
                                    end) desc) as rank
    FROM cd.facilities fac
    INNER JOIN cd.bookings book
        ON book.facid=fac.facid
    GROUP BY fac.name
)

SELECT name, rank
FROM ranking_obiektow
WHERE rank <= 3
ORDER BY rank, name;

//exercise 20-Aggregates
//similar exercise with classes and ntitle(3)-cuts function in 3
select name, case when class=1 then 'high'
		when class=2 then 'average'
		else 'low'
		end revenue
	from (
		select facs.name as name, ntile(3) over (order by sum(case
				when memid = 0 then slots * facs.guestcost
				else slots * membercost
			end) desc) as class
		from cd.bookings bks
		inner join cd.facilities facs
			on bks.facid = facs.facid
		group by facs.name
	) as subq
order by class, name;


-- CTE section: rewritten from nested subqueries for readability

//exercise 8-joins and subqueries (CTE version)
//rewritten from nested subquery in FROM to a named CTE
WITH booking_costs AS (
    SELECT
        mems.firstname || ' ' || mems.surname AS member,
        facs.name AS facility,
        CASE
            WHEN mems.memid = 0 THEN bks.slots * facs.guestcost
            ELSE bks.slots * facs.membercost
        END AS cost
    FROM cd.members mems
    INNER JOIN cd.bookings bks ON mems.memid = bks.memid
    INNER JOIN cd.facilities facs ON bks.facid = facs.facid
    WHERE bks.starttime >= '2012-09-14' AND bks.starttime < '2012-09-15'
)
SELECT member, facility, cost
FROM booking_costs
WHERE cost > 30
ORDER BY cost DESC;

//exercise 10-Aggregates (CTE version)
//rewritten from nested subquery in FROM to a named CTE
WITH booking_revenue AS (
    SELECT fac.name,
           SUM(slots * CASE
                   WHEN memid = 0 THEN fac.guestcost
                   ELSE fac.membercost
               END) AS revenue
    FROM cd.bookings book
    INNER JOIN cd.facilities fac
        ON fac.facid = book.facid
    GROUP BY fac.name
)
SELECT name, revenue
FROM booking_revenue
WHERE revenue > 1000
ORDER BY revenue;

//exercise 20-Aggregates (CTE version)
//rewritten from nested subquery in FROM to a named CTE
WITH subq AS (
    SELECT facs.name AS name,
           NTILE(3) OVER (
               ORDER BY SUM(CASE
                   WHEN memid = 0 THEN slots * facs.guestcost
                   ELSE slots * membercost
               END) DESC
           ) AS class
    FROM cd.bookings bks
    INNER JOIN cd.facilities facs
        ON bks.facid = facs.facid
    GROUP BY facs.name
)
SELECT name,
       CASE
           WHEN class = 1 THEN 'high'
           WHEN class = 2 THEN 'average'
           ELSE 'low'
       END AS revenue
FROM subq
ORDER BY class, name;

//exercise 3- recursive 
//CTE-type, recursive exercise
with recursive recommenders(recommender, member) as (
	select recommendedby, memid
		from cd.members
	union all
	select mems.recommendedby, recs.member
		from recommenders recs
		inner join cd.members mems
			on mems.memid = recs.recommender
)
select recs.member member, recs.recommender, mems.firstname, mems.surname
	from recommenders recs
	inner join cd.members mems
		on recs.recommender = mems.memid
	where recs.member = 22 or recs.member = 12
order by recs.member asc, recs.recommender desc


-- sql exercises with pagilla

-- 1. Top 3 Films by Rating per Category
WITH ranked_films AS (
    SELECT
        fi.title,
        fi.rating,
        cat.name AS category_name,
        ROW_NUMBER() OVER (
            PARTITION BY cat.name
            ORDER BY fi.rating DESC
        ) AS ranking
    FROM film fi
    INNER JOIN film_category fcat
        ON fi.film_id = fcat.film_id
    INNER JOIN category cat
        ON cat.category_id = fcat.category_id
)
SELECT
    title,
    rating,
    category_name
FROM ranked_films
WHERE ranking <= 3;


-- 2. Daily Cumulative Running Total
SELECT
    payment_date::DATE AS payment_day,
    SUM(amount) AS daily_revenue,
    SUM(SUM(amount)) OVER (ORDER BY payment_date::DATE) AS cumulative_revenue
FROM payment
GROUP BY payment_date::DATE
ORDER BY payment_day;


-- 3. 7-Day Moving Average of Daily Revenue
SELECT
    payment_date::DATE AS payment_day,
    SUM(amount) AS daily_revenue,
    AVG(SUM(amount)) OVER (
        ORDER BY payment_date::DATE
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d
FROM payment
GROUP BY payment_date::DATE
ORDER BY payment_day;


-- 4. Month-over-Month (MoM) Revenue Growth Percentage
WITH monthly_summary AS (
    SELECT
        TO_CHAR(payment_date, 'YYYY-MM') AS payment_month,
        SUM(amount) AS monthly_revenue
    FROM payment
    GROUP BY TO_CHAR(payment_date, 'YYYY-MM')
)
SELECT
    payment_month,
    monthly_revenue,
    LAG(monthly_revenue) OVER (ORDER BY payment_month) AS previous_month_revenue,
    ROUND(
        (monthly_revenue / LAG(monthly_revenue) OVER (ORDER BY payment_month) - 1) * 100,
        2
    ) AS mom_growth_pct
FROM monthly_summary
ORDER BY payment_month;


-- 5. Customer Revenue Contribution Share
SELECT
    customer_id,
    SUM(amount) AS customer_revenue,
    SUM(SUM(amount)) OVER () AS total_revenue,
    ROUND(
        (SUM(amount) / SUM(SUM(amount)) OVER ()) * 100,
        2
    ) AS revenue_share_pct
FROM payment
GROUP BY customer_id
ORDER BY revenue_share_pct DESC;


-- 6. First and Last Rental Date per Customer
SELECT
    customer_id,
    MIN(rental_date) AS first_rental_date,
    MAX(rental_date) AS last_rental_date
FROM rental
GROUP BY customer_id
ORDER BY customer_id;


-- 7. Customer Deciles by Total Spend (NTILE)
WITH customer_spend AS (
    SELECT
        customer_id,
        SUM(amount) AS total_spent
    FROM payment
    GROUP BY customer_id
)
SELECT
    customer_id,
    total_spent,
    NTILE(10) OVER (ORDER BY total_spent DESC) AS decile
FROM customer_spend
ORDER BY decile, total_spent DESC;


