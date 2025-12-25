class Game:
    __slots__ = ("_appid", "_name", "_release_date", "_price", "_metascore", "_url")

    def __init__(
        self,
        appid: int,
        name: str | None = None,
        release_date: str | None = None,
        price: str | None = None,
        metascore: int | None = None,
        url: str | None = None,
    ):
        self._appid = appid
        self._name = name
        self._release_date = release_date
        self._price = price
        self._metascore = metascore
        self._url = url

    def to_dict(self) -> dict:
        return {slot: getattr(self, slot) for slot in self.__slots__}

    def __repr__(self) -> str:
        return f"Game(appid={self._appid}, name={self._name}, release_date={self._release_date}, price={self._price}, metascore={self._metascore}, url={self._url})"
    
    def __str__(self) -> str:
        return f"{self._name} ({self._appid})"

    @property
    def appid(self) -> int:
        return self._appid
    
    @property
    def name(self) -> str | None:
        return self._name
    
    @property
    def release_date(self) -> str | None:
        return self._release_date
    
    @property
    def price(self) -> str | None:
        return self._price
    
    @property
    def metascore(self) -> int | None:
        return self._metascore
    
    @property 
    def url(self) -> str | None:
        return self._url
