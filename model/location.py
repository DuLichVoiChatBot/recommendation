class Location:
    def __init__(self) -> None:
        pass

    def __init__(self, ID, Name, Address, Category, Description, Price, Type, Url, Tags):
        self.ID = ID
        self.Name = Name
        self.Address = Address
        self.Category = Category
        self.Description = Description
        self.Price = Price
        self.Type = Type
        self.Url = Url
        self.Tags = Tags

    def __str__(self) -> str:
        pass
    