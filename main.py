from datetime import datetime
from mangum import Mangum 
from typing import List,Optional,Any
from fastapi import FastAPI,File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from pydantic import BaseModel
import cloudinary
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine,Column, String, Integer, ARRAY, Boolean,DateTime,JSON
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


app = FastAPI()
# handler=Mangum(app)

username = 'postgres'
password = 'admin'
host = 'localhost'
port = '5433'  # Par défaut, le port PostgreSQL est 5432
database_name = 'hero'

# Créez l'URL de connexion PostgreSQL
db_url ='postgresql://bricebrain:uoIdVeUb2Ci4@ep-odd-block-55907706.eu-central-1.aws.neon.tech/optimusprimedb?sslmode=require'

#db_url =f'postgresql://{username}:{password}@{host}:{port}/{database_name}'


# f'postgresql://{username}:{password}@{host}:{port}/{database_name}'


engine = create_engine(db_url)
# Créer la table



Base = declarative_base()

    
class TableArticles(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
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
    
    
class TableCommande(Base):
    __tablename__ = "commandes"
    
    id = Column(Integer, primary_key=True, index=True)
    civility = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    address = Column(String)
    phone = Column(String) 
    email = Column(String)
    cart = Column(ARRAY(JSON), default=[])
    status = Column(String)
    total= Column(Integer)
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
    id : Optional[int] = None
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

    
 
class Commande(BaseModel): 
    id : Optional[int] = None
    civility :str
    firstname:str
    lastname :str
    address :str
    phone :str
    email :Optional[str] = None
    status :str
    cart :Any
    total:float
    created : Optional[datetime] = None
    updated : Optional[datetime] = None   


    
    
class UpdateStatus(BaseModel): 
    status :str
   
   



db = SessionLocal()



origins = ["*"]  # Ajoutez les origines autorisées
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    
    # sessionmaker(autocommit=False, autoflush=True, bind=engine)()
    try:
        yield db
    finally:
        db.close()



class User (BaseModel):
    name :str
    age : int
    

@app.get("/",response_model=str, status_code=200)
async def root():
    return "items"

@app.get("/articles",response_model=List[Articles], status_code=200)
async def getArticles():
    items = db.query(TableArticles).filter(TableArticles.status == "ACTIVE").all()
    return items

@app.get("/commandes",response_model=List[Commande], status_code=200)
async def getArticles():
    items = db.query(TableCommande).all()
    return items


@app.post("/addArticles",response_model=Articles, status_code=201)
async def add(article:Articles):
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
    db.commit()
    return new_article

@app.post("/addCommande",response_model=Commande, status_code=201)
async def addCommande(commande:Commande):
    new_commande = TableCommande(
        civility=commande.civility,
        firstname=commande.firstname,
        lastname = commande.lastname,
        address = commande.address,
        phone = commande.phone,
        email = commande.email,
        status = commande.status,
        cart = commande.cart,
        total = commande.total
        )
    db.add(new_commande)
    db.commit()
    return new_commande


@app.put("/updateCommande/{id}",response_model=Commande, status_code=201)
async def updateArticles(id:int,status:str ):
        items = db.query(TableCommande).filter(TableCommande.id == id).first()
        items.status = status
        items.updated = datetime.utcnow()

        db.commit()
        return items


@app.put("/updateArticle/{id}",response_model=Articles, status_code=201)
async def updateArticles(id:int,article:Articles ):
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
async def updateArticles(id:int,data:UpdateStatus ):
        items = db.query(TableArticles).filter(TableArticles.id == id).first()
        items.status = data.status
        items.updated = datetime.utcnow()
        db.commit()
        return items

    
@app.post("/uploadfilesMulti/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    try:
        urls = []
        for file in files:
            # Utilisez Cloudinary pour télécharger chaque fichier
            response = upload(file.file, folder="dossierAkf")

            # Utilisez cloudinary_url pour obtenir l'URL public du fichier téléchargé
            url, options = cloudinary_url(response['public_id'], format=response['format'])
            urls.append(url)

        return JSONResponse(content={"urls": urls}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
