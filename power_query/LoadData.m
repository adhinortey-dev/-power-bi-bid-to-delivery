// Set DataFolder to the absolute path to this package's data folder.
// Create each section as a separate Blank Query in Power BI Desktop.

// Query name: Projects
let
    DataFolder = "C:\PATH\TO\PowerBI_Portfolio_Rebar_Analytics\data",
    Source = Csv.Document(
        File.Contents(DataFolder & "\Projects.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"ProjectID", type text}, {"QuoteDate", type date}, {"BidDeadline", type date},
        {"AwardDate", type date}, {"DeliveryDate", type date}, {"Customer", type text},
        {"Region", type text}, {"CustomerSegment", type text}, {"ProjectType", type text},
        {"Estimator", type text}, {"Stage", type text}, {"QuotedTons", type number},
        {"QuoteAmount", Currency.Type}, {"EstimatedCost", Currency.Type},
        {"AwardedTons", type number}, {"ActualCost", Currency.Type}, {"Priority", type text}
    }, "en-US")
in
    Types

// Query name: DimProject (create as a reference query from Projects)
let
    Source = Projects,
    Selected = Table.SelectColumns(Source, {
        "ProjectID", "Customer", "Region", "CustomerSegment", "ProjectType",
        "Estimator", "Stage", "Priority"
    }),
    UniqueProjects = Table.Distinct(Selected, {"ProjectID"})
in
    UniqueProjects

// Query name: Shipments
let
    DataFolder = "C:\PATH\TO\PowerBI_Portfolio_Rebar_Analytics\data",
    Source = Csv.Document(
        File.Contents(DataFolder & "\Shipments.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"ShipmentID", type text}, {"ProjectID", type text},
        {"PlannedShipDate", type date}, {"ActualShipDate", type date},
        {"ShipmentTons", type number}, {"ShipmentStatus", type text}
    }, "en-US")
in
    Types
