from datetime import datetime
from typing import List,Optional,Any
from fastapi import FastAPI,File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from pydantic import BaseModel
import cloudinary
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine,Column, String, Integer, ARRAY, Boolean,DateTime,JSON,ForeignKey,desc,asc
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship,joinedload, Session


app = FastAPI()


username = 'postgres'
password = 'admin'
host = 'localhost'
port = '5433'  # Par défaut, le port PostgreSQL est 5432
database_name = 'hero'

# Créez l'URL de connexion PostgreSQL
db_url ='postgresql://bricebrain:uoIdVeUb2Ci4@ep-odd-block-55907706.eu-central-1.aws.neon.tech/optimusprimedb?sslmode=require'

#db_url =f'postgresql://{username}:{password}@{host}:{port}/{database_name}'


# f'postgresql://{username}:{password}@{host}:{port}/{database_name}'


engine = create_engine(db_url, pool_size=10, max_overflow=20)
# Créer la table



Base = declarative_base()

    
class TableArticles(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    brand = Column(String)
    price = Column(Integer)
    description = Column(String)
    color = Column(ARRAY(String))  
    size = Column(ARRAY(String))  
    category = Column(String)
    isBestseller = Column(Boolean)
    status = Column(String)
    stock = Column(Integer)
    picture =Column(ARRAY(String))  
    created =  Column(DateTime, default=datetime.utcnow)
    updated =  Column(DateTime, default=datetime.utcnow)

class TableClient(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    gender = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    address = Column(String)
    email = Column(String)
    phone = Column(String)
    favoris =Column(ARRAY(Integer))  
    password = Column(String)
    status = Column(String)
    type = Column(String)
    picture = Column(String)
    commandes = relationship("TableCommande", back_populates="client")
    created =  Column(DateTime, default=datetime.utcnow)
    updated =  Column(DateTime, default=datetime.utcnow)
    
    
class TableCommande(Base):
    __tablename__ = "commandes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    clientId =  Column(Integer, ForeignKey("clients.id"))
    cart = Column(ARRAY(JSON), default=[])
    status = Column(String)
    total= Column(Integer)
    client = relationship("TableClient", back_populates="commandes")
    created =  Column(DateTime, default=datetime.utcnow)
    updated =  Column(DateTime, default=datetime.utcnow)
    
    

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



          
cloudinary.config( 
  cloud_name = "dqhr2l0wr", 
  api_key = "278625252113383", 
  api_secret = "je5ACt_Mag3tM8-5tTDCTbk8gJE" 
)



    
# Configuration de la base de données
class Perso(BaseModel):
    id:Optional[int] = None
    namePerso:str
    age:int
    
    # class Config:
    #     orm_mode=True
    
class Articles(BaseModel): 
    id: Optional[int] = None
    brand :str
    price:float
    isBestseller :bool
    category :str
    color :Optional[List[str]] = None
    description :str
    status :str
    size :Optional[List[str]] = None
    stock:int
    picture :List[str]
    created : Optional[datetime] = None
    updated : Optional[datetime] = None
    


class Cart(BaseModel): 
    id : Optional[int] = None
    brand :str
    category:str
    color :Optional[List[str]] = None
    description :str
    picture :List[str] = None
    price :float
    quantity:int
    size:Optional[str] = None
    status :str

    
 

 
    
    
class Client(BaseModel): 
    id : Optional[int] = None
    gender : str 
    firstname  : str 
    lastname  : str 
    address  : str 
    email : str 
    phone  : str 
    favoris :List[int] = None
    password : str 
    status : str 
    type : str 
    picture : Optional[str] = None 
    created : Optional[datetime] = None
    updated : Optional[datetime] = None   
    
class ClientTruncate(BaseModel): 
    id : Optional[int] = None
    gender : str 
    firstname  : str 
    lastname  : str 
    address  : str 
    email : str 
    phone  : str 
    favoris :List[int] = None
    status : str 
    type : str 
    picture : Optional[str] = None 
    created : Optional[datetime] = None
    updated : Optional[datetime] = None   

class Commande(BaseModel): 
    id : Optional[int] = None
    clientId :int
    status :str
    cart :Any
    total:float
    created : Optional[datetime] = None
    updated : Optional[datetime] = None  
    client: Optional[Client] = None
    
    
class UpdateStatus(BaseModel): 
    status :str
   
   







origins = ["http://localhost", "http://localhost:3000","http://localhost:3001", "http://localhost:5173",  "https://akfprestige.vercel.app"]  # Ajoutez les origines autorisées
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine(
    db_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,   # important sur Render
    pool_recycle=1800,    # évite connexions mortes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()



class User (BaseModel):
    name :str
    age : int
    
class ConnexionUser (BaseModel):
    email :str
    password : str
    

@app.get("/",response_model=str, status_code=200)
def root():
    return "items"

@app.get("/articles",response_model=List[Articles], status_code=200)
def getArticles(db: Session = Depends(get_db)):
    items = db.query(TableArticles).filter(TableArticles.status == "ACTIVE"). all()
    return items

@app.get("/clients",response_model=List[Client], status_code=200)
def getClients(db: Session = Depends(get_db)):
    items = db.query(TableClient). all()
    return items

@app.get("/stockArticles",response_model=List[Articles], status_code=200)
def getArticles(db: Session = Depends(get_db)):
    items = db.query(TableArticles).filter(TableArticles.status == "ACTIVE").order_by(asc(TableArticles.stock)).all()
    return items



@app.get("/commandes",response_model=List[Commande], status_code=200)
def getCommandes(db: Session = Depends(get_db)):
    items = db.query(TableCommande).order_by(desc(TableCommande.updated)).all()
    return items

@app.get("/analyse",response_model=Any, status_code=200)
def analyse(db: Session = Depends(get_db)):
    items = db.query(TableCommande).filter(TableCommande.status == "PAYE").all()
    analyse ={
        "montant_total":0,
        "BAG":0,
        "CLOTHING":0,
        "CARE":0,
        "BEAUTY_AND_ACCESORIES":0
    }
    
    top_ventes ={  }
  
    
    for item in items : 
        analyse['montant_total']+= item.total
        for article in item.cart:
            valeur = article.get('id')
            category = article.get('category')
            analyse[category] =  analyse[category]  +1
            print(valeur)
            # id= article['id']
            if top_ventes.get(valeur) :
                top_ventes[valeur]=  top_ventes[valeur] + 1
            else:
                top_ventes[valeur]=1
            # analyse[article['category']]+=1
    
    
    return [top_ventes, analyse]



@app.post("/addArticles",response_model=Articles, status_code=201)
def addArticles(article:Articles, db: Session = Depends(get_db)):
    new_article = TableArticles(
        brand=article.brand,
        price=article.price,
        isBestseller = article.isBestseller,
        category = article.category,
        description = article.description,
        status = article.status,
        stock = article.stock,
        picture = article.picture
        )
    db.add(new_article)
    db.flush()      # pour obtenir new_article.id si besoin
    db.refresh(new_article)
    return new_article


@app.post("/tryToConnect",response_model=ClientTruncate, status_code=201)
def tryToConnect(info:ConnexionUser,  db: Session = Depends(get_db)):
    user = db.query(TableClient).filter(TableClient.email == info.email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Client not found")
    if user.password != info.password :
        raise HTTPException(status_code=404, detail="password invalid")
    return user
            
@app.post("/createAccount",response_model=ClientTruncate, status_code=201)
def createAccount(client:Client,  db: Session = Depends(get_db)):
    new_account = TableClient(
        gender =client.gender,
        firstname =client.firstname,
        lastname =client.lastname,
        address =client.address,
        email =client.email,
        phone =client.phone,
        favoris =client.favoris,
        password =client.password,
        status =client.status,
        type =client.type
        )
    db.add(new_account)
    db.commit()
    return new_account

@app.put("/updateClientFav/{id}",response_model=Client, status_code=201)
def updateClientFav(id:int,tabFav:List[int],  db: Session = Depends(get_db) ):
        items = db.query(TableClient).filter(TableClient.id == id).first()
        items.favoris = tabFav
        items.updated = datetime.utcnow()

        db.commit()
        return items


# @app.get("/allCommande",response_model=List[Commande], status_code=200)
# async def allCommande():
#     allcommande =  db.query(TableCommande).options(joinedload(TableCommande.clientId)).all()
#     print(allcommande)
#     return allcommande


@app.post("/addCommande",response_model=Commande, status_code=201)
def addCommande(commande:Commande,  db: Session = Depends(get_db)):
    new_commande = TableCommande(
        clientId =  commande.clientId,
        status = commande.status,
        cart = commande.cart,
        total = commande.total
        )
    db.add(new_commande)
   
    for item in commande.cart:
        article = db.query(TableArticles).filter(TableArticles.id == item["id"]).with_for_update().first()
        if not article:
            raise HTTPException(status_code=404, detail=f"Article {item['id']} introuvable")
        if article.stock < item["quantity"]:
            raise HTTPException(status_code=400, detail=f"Stock insuffisant pour l'article {item['id']}")
        article.stock -= item["quantity"]

    db.flush()
    db.refresh(new_commande)
    return new_commande


@app.put("/updateCommande/{id}",response_model=Commande, status_code=201)
def updateArticles(id:int,status:str ,  db: Session = Depends(get_db)):
        items = db.query(TableCommande).filter(TableCommande.id == id).first()
        items.status = status
        items.updated = datetime.utcnow()

        db.commit()
        return items


@app.put("/updateArticle/{id}",response_model=Articles, status_code=201)
def updateArticles(id:int,article:Articles ,  db: Session = Depends(get_db)):
        items = db.query(TableArticles).filter(TableArticles.id == id).first()
        items.brand=article.brand
        items.price=article.price
        items.isBestseller = article.isBestseller
        items.category = article.category
        items.description = article.description
        items.status = article.status
        items.stock = article.stock
        items.picture = article.picture
        items.updated = datetime.utcnow()
        

        db.commit()
        return items
    
@app.put("/delete/{id}",response_model=Articles, status_code=201)
def updateArticles(id:int,data:UpdateStatus,  db: Session = Depends(get_db) ):
        items = db.query(TableArticles).filter(TableArticles.id == id).first()
        items.status = data.status
        items.updated = datetime.utcnow()
        db.commit()
        return items

    
@app.post("/uploadfilesMulti/")
def create_upload_files(files: List[UploadFile] = File(...),  db: Session = Depends(get_db)):
    try:
        urls = []
        for file in files:
            # Utilisez Cloudinary pour télécharger chaque fichier
            response = upload(file.file, folder="dossierAkf")

            # Utilisez cloudinary_url pour obtenir l'URL public du fichier téléchargé
            url, options = cloudinary_url(response['public_id'], format=response['format'])
            format_url = url.replace("http://", "https://")
            
            urls.append(format_url)

        return JSONResponse(content={"urls": urls}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
