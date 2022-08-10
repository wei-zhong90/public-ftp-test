package main

import (
	"fmt"
	"log"
	"os"
	"strconv"
	"time"

	"github.com/google/uuid"
	"github.com/jlaffaye/ftp"
)

var passwd string = "19901022Zw!"

const timeout = 60 * time.Second

func upload_file(host string, user string, result chan string, errChan chan error, timeMonitor chan map[string]time.Duration) error {

	start := time.Now()

	c, err := ftp.Dial(host, ftp.DialWithTimeout(300*time.Second))
	if err != nil {
		log.Fatal(err)
	}

	err = c.Login(user, passwd)
	if err != nil {
		log.Fatal(err)
	}

	// Do something with the FTP conn
	data, err := os.Open("sample_data.zip")
	if err != nil {
		log.Fatal(err)
	}
	fileName, err := uuid.New().MarshalText()
	nameString := string(fileName)
	if err != nil {
		log.Fatal(err)
	}

	err = c.Stor(nameString, data)
	if err != nil {
		log.Println(err)
		errChan <- err
		timeMonitor <- map[string]time.Duration{"error": time.Since(start)}
		return err
	}

	if err := c.Quit(); err != nil {
		log.Fatal(err)
	}
	result <- nameString
	timeMonitor <- map[string]time.Duration{"success": time.Since(start)}
	return nil
}

func average(array []time.Duration) uint8 {
	result := time.Duration(0)
	for _, v := range array {
		result += v
	}
	resultInInt := int(result.Seconds())
	return uint8(resultInInt / len(array))
}

func main() {
	var host string = os.Args[1]
	var user string = os.Args[2]
	concurrency, err := strconv.Atoi(os.Args[3])
	if err != nil {
		log.Fatal(err)
	}
	result := make(chan string, concurrency)
	errChan := make(chan error)
	timeMonitor := make(chan map[string]time.Duration)

	timec := time.After(timeout)

	for i := 0; i < concurrency; i++ {
		go upload_file(host, user, result, errChan, timeMonitor)
	}

	counter := 1
	errCounter := 0
	var execTimeList []time.Duration
RangeLoop:
	for {
		select {
		case <-timec:
			break RangeLoop // timed out
		case name, ok := <-result:
			if !ok {
				break RangeLoop // Channel closed
			}
			log.Printf("FILE No %d\n%s is uploading ...", counter, name)
			counter++
		case <-errChan:
			errCounter++
		case monitor, ok := <-timeMonitor:
			if !ok {
				break RangeLoop // Channel closed
			}
			if val, ok := monitor["success"]; ok {
				execTimeList = append(execTimeList, val)
			}
		}
	}
	uploadedNumber := counter - 1

	fmt.Print("\n\n##############################\n")
	log.Printf("Within 1 minute uploads:")
	log.Printf("\tThe average upload time for %d successful uploads: %ds", uploadedNumber, average(execTimeList))
	log.Printf("\tIn total %d FILES failed", errCounter)

}
