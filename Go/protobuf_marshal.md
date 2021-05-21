
## protobuf 에서 proto 의 message 에 정의된 내용을 marshal

marshal 은 codec 을 통한 encoding ( codec marshal ) 

codec 은 기본적으로

newClientStream -> setCallInfoCodec 에서 codec 로 marshal, unmarshal 하여 사용함.

encoding.RegisterCodec 함수에 커스텀해서 등록해서 사용할 수 있음
```go
type Codec interface {
	// Marshal returns the wire format of v.
	Marshal(v interface{}) ([]byte, error)
	// Unmarshal parses the wire format into v.
	Unmarshal(data []byte, v interface{}) error
	// Name returns the name of the Codec implementation. The returned string
	// will be used as part of content type in transmission.  The result must be
	// static; the result cannot change between calls.
	Name() string
}
```
위 인터페이스 만족하면 ok 

기본적으로 grpc 의 경우

grpc/encoding/proto/proto.go 파일에 있는 marshaler 를 사용하는데 ( Name = “proto” ) 
해당 marshaler 에서 protoV2 MarshalAppend 에서 marshal 을 함 ( protobuf api v2 기준 )

MarshalAppend 안에서 reflect 된 message 기준으로 

메소드를 찾아 marshal 을 하는데 이때

#### ***** 정렬된 필드 순서 ( 메시지에 정의한 넘버 순서 ) 대로 buffer 에 값을 넣음 ***** 

먼저 field 의 offset 을 버퍼에 넣고 그다음 protobuf/internal/impl 안의 각각의 codec type 별로 값을 bytes 로 가져온 후 버퍼에 담음

이 순서대로 버퍼에 하나씩 값을 넣음

그렇기 떄문에 number 를 이런형태로 활용하는것을 알 수 있음

### field 의 offset 은 무슨 값일까? 
위의 메소드를 찾는 부분에서 protoMethod 호출
makeCoderMethods 안에서
fieldOffset 을 가져오는데

field offset 값은 fieldsByNumber 에 있고 이 값은

proto message struct init 과정에서 struct field 에 저장이 되있는 태그 ( ex `protobuf:”xxx”`) 값 으로 
순서 결정을 하고 

offset 은 offsetEmbed >> 1 로 사용됨 
테스트 중인 메시지 값은 offsetEmbed (0, 16, 32, 80, 96, 128) 값이 있었으며

80 부터 값이 있음 ( state, sizeCache, unknownFields 는 pass 되기 때문에.[0,16,32] )

고로 80, 96, 128 의 값의 쉬프트 연산 ( >> 1 )으로 인해
실제 offset 은 40, 48, 64 값으로 되었음을 확인 



+++ 먼가 대충 써놓은 느낌이라 나중에 정리가 좀 
