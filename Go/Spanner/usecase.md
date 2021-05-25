
## Mutation 을 활용한 경우
spanner.InsertStruct, spanner.UpdateStruct, spanner.Delete(table, spanner.Key{}) 등등  
Mutation 을 통하여 ReadWriteTransaction 에 Write 할 때에는 
#### PK 로 등록한 모든 필드가 필수적으로 전부 포함 되어야함!  

`a, b, c 값이 pk 일 경우 Key{} 의 경우 순서대로 전부 포함되어야 하고 Struct 를 통한 ORM 사용 경우 해당 테이블의 PK 이름 값이 모두 포함되어야 함`

---

## Mutation 을 사용할 수 없는 경우
a,b,c 값이 pk 인데 a 값이 일치하는 데이터를 전부 삭제하고 싶을때에는 Statement 를 활용해야함.

```go
stmt := spanner.Statement{
	SQL:    fmt.Sprintf("DELETE FROM %s WHERE a = @a”, table),
	Params: map[string]interface{}{“a”: “1234”},
}
```
와 같이 Statement 를 담아 쿼리로 실행 시켜야 하며  

client.ReadWriteTransaction 의 transaction.BatchUpdate or transaction.Update 를 활용 
