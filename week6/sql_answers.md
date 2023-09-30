1.59
SELECT COUNT(*) from customers

2.Rock
SELECT tmp.GenreId
       ,g.name
FROM (SELECT t.GenreId
       	     ,SUM(i.Quantity)
      FROM invoice_items i
      LEFT JOIN tracks t
      ON i.trackId = t.trackId
      GROUP BY genreId
      ORDER BY SUM(Quantity) DESC
      )
AS tmp
LEFT JOIN genres g
ON tmp.GenreId = g.GenreId

3. Two answers: Rock and Roll, Sience Fiction
SELECT tmp.GenreId
       ,g.name
FROM (SELECT t.GenreId
       	     ,SUM(i.Quantity)
      FROM invoice_items i
      LEFT JOIN tracks t
      ON i.trackId = t.trackId
      GROUP BY genreId
      ORDER BY SUM(Quantity) ASC
      )
AS tmp
LEFT JOIN genres g
ON tmp.GenreId = g.GenreId


4. Iron Maiden
SELECT tmp.name, COUNT(i.Quantity) AS total FROM invoice_items i
LEFT JOIN(SELECT ar.Name, t.TrackId FROM artists ar
LEFT JOIN albums al ON ar.ArtistId = al.ArtistID
LEFT JOIN tracks t ON al.AlbumId = t.AlbumId) AS tmp 
ON i.TrackId=tmp.TrackId
GROUP BY tmp.Name
ORDER BY total DESC


5. 3
SELECT ar.Name,COUNT(al.AlbumId) FROM artists ar
LEFT JOIN albums al ON ar.ArtistId =  al.ArtistId
WHERE ar.Name = 'Miles Davis'
GROUP BY ar.ArtistId 


6. Occupation / Precipice
SELECT NAME, Milliseconds FROM tracks ORDER BY MIlliseconds DESC


7. Lost, Season 3
SELECT	title, totalTime FROM albums a
LEFT JOIN
(SELECT AlbumId
        ,SUM(Milliseconds) totalTime
FROM tracks GROUP BY AlbumId) t
ON t.AlbumId = a.AlbumId
ORDER BY totalTime DESC


8. 404, 25.86, Helena Holý
SELECT i.InvoiceId
	,total
	,c.FirstName
	,c.LastName
FROM invoices i
LEFT JOIN customers c ON i.CustomerId = c.CustomerId 
ORDER BY total DESC;


9.Helena Holý
SELECT c.CustomerId
	,SUM(Total)
	,c.FirstName
	,c.LastName
FROM customers c
LEFT JOIN invoices i ON c.CustomerId = i.CustomerId
GROUP BY c.CustomerId
ORDER BY SUM(Total) DESC;