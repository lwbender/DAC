	select 
	d.SerialNumber
--	,p.[FirstName]
--	,p.[LastName]
--	,drm.
	,'Base Station Name' = ea.name
	,rm.[MeasurementTransactionID]
    ,'Status' = [StatusRegister]
	,'PC0' = convert(real,rmv0.Amount)
	,'PC1' = convert(real,rmv1.Amount)/2097152*220000
	,'PC2' = convert(real,rmv2.Amount)/2097152*220000
	,'PC3' = convert(real,rmv3.Amount)/2097152*220000
	,'PC4' = convert(real,rmv4.Amount)/2097152*220000
	,'PC5' = convert(real,rmv5.Amount)/2097152*220000
	,'PC6' = convert(real,rmv6.Amount)/2097152*220000
	,'PC7' = convert(real,rmv7.Amount)/2097152*220000
	,'Al Temp' = convert(real,rm.ExternalTemp)/2097152
	,'Pt Temp' = convert(real,rm.[InternalTemp])/2097152
	,'Thermistor_Celsius' = -13.5260795812 + (337.400560235)*(rmv7.Amount/2097152) + (-1300.06056511)*(rmv7.Amount/2097152)*(rmv7.Amount/2097152) + (2039.85355830)*(rmv7.Amount/2097152)*(rmv7.Amount/2097152)*(rmv7.Amount/2097152) + (-476.078532986)*(rmv7.Amount/2097152)*(rmv7.Amount/2097152)*(rmv7.Amount/2097152)*(rmv7.Amount/2097152)
	,'MeasurementTimeStamp' =  rm.[MeasurementDate]
	,'ServerTimeStamp' = rm.[ServerTimeStamp]
	,'Motion' = rm.MotionDetectionCounter
from 
	[dbo].[RawMeasurement]			rm
	,[dbo].[EquipmentActivations]	ea
	,[dbo].[Dosimeters]				d
	,[dbo].[RawMeasurementValues]	rmv0
	,[dbo].[RawMeasurementValues]	rmv1
	,[dbo].[RawMeasurementValues]	rmv2
	,[dbo].[RawMeasurementValues]	rmv3
	,[dbo].[RawMeasurementValues]	rmv4
	,[dbo].[RawMeasurementValues]	rmv5
	,[dbo].[RawMeasurementValues]	rmv6
	,[dbo].[RawMeasurementValues]	rmv7
--	,[dbo].[Participants]			p
Where
	d.SerialNumber = 'VA00002980T'
--	ea.Name = 'Kimball HALT Testing'
--	and drm.[MeasurementDate] > '8/29/2016'
--	and rm.MeasurementTransactionID >= 1745
	and d.[DosimeterID] = rm.[DosimeterID]
	and rmv0.RawMeasurementID = rm.RawMeasurementID
	and rmv1.RawMeasurementID = rm.RawMeasurementID
	and rmv2.RawMeasurementID = rm.RawMeasurementID
	and rmv3.RawMeasurementID = rm.RawMeasurementID
	and rmv4.RawMeasurementID = rm.RawMeasurementID
	and rmv5.RawMeasurementID = rm.RawMeasurementID
	and rmv6.RawMeasurementID = rm.RawMeasurementID
	and rmv7.RawMeasurementID = rm.RawMeasurementID
	and rmv0.SensorTypeID = 1
	and rmv1.SensorTypeID = 2
	and rmv2.SensorTypeID = 3
	and rmv3.SensorTypeID = 4
	and rmv4.SensorTypeID = 5
	and rmv5.SensorTypeID = 6
	and rmv6.SensorTypeID = 7
	and rmv7.SensorTypeID = 8
	and ea.[EquipmentActivationID] = rm.[EquipmentActivationID]
	
Order by
	rm.[ServerTimeStamp] desc
--	drm.MeasurementTransactionID
--	d.SerialNumber
--	drm.[MeasurementDate] desc
