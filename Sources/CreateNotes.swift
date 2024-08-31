import Algorithms
import ArgumentParser
import Foundation

struct MinimalPairComponent {
	let distinctiveFeature: String
	let word: String
}

struct FPTAITextToSpeechResponse: Decodable {
	let async: URL
	let error: Int
	let message, requestID: String

	enum CodingKeys: String, CodingKey {
		case async, error, message
		case requestID = "request_id"
	}
}

@main
struct CreateNotes: AsyncParsableCommand {
	@Argument(completion: .file(), transform: URL.init(fileURLWithPath:))
	var minimalPairComponentsFile: URL

	@Argument()
	var apiKey: String

	@Argument(completion: .directory, transform: URL.init(fileURLWithPath:))
	var mediaDirectory: URL


	func downloadMissingAudioFiles(minimalPairComponents: [MinimalPairComponent]) async throws {
		let jsonDecoder = JSONDecoder()
		for minimalPairComponent in minimalPairComponents {
			let filename = "tts-\(minimalPairComponent.word).mp3"
			let audioExists = FileManager.default.fileExists(
				atPath: self.mediaDirectory
					.appending(component: filename)
					.path()
			)
			if !audioExists {
				var request = URLRequest(url: URL(string: "https://api.fpt.ai/hmi/tts/v5")!)
				request.httpMethod = "POST"
				request.setValue(self.apiKey, forHTTPHeaderField: "api-key")
				request.setValue("0.5", forHTTPHeaderField: "speed")
				request.setValue("banmai", forHTTPHeaderField: "voice")

				let (responseData, response) = try await URLSession.shared.upload(
					for: request,
					from: Data(minimalPairComponent.word.utf8)
				)

				guard let httpResponse = response as? HTTPURLResponse,
						(200...299).contains(httpResponse.statusCode) else {
					print("Error getting \"\(minimalPairComponent.word)\"")
					continue
				}
				let welcome = try jsonDecoder.decode(FPTAITextToSpeechResponse.self, from: responseData)
				print(welcome.async)
			}
		}
	}
	func exportCSVFile(minimalPairComponents: [MinimalPairComponent]) throws {

		let csvContent = minimalPairComponents
			.combinations(ofCount: 2)
			.reduce("") { partialResult, minimalPair in
				partialResult + "\n\(minimalPair[0].distinctiveFeature);\(minimalPair[0].word);\(minimalPair[1].distinctiveFeature);\(minimalPair[1].word)"
			}
			.trimmingCharacters(in: .whitespacesAndNewlines)

		let dateFormatter = DateFormatter()
		dateFormatter.dateFormat = "YY-MM-dd-HH-mm-ss"

		let exportDirectory = URL.desktopDirectory
			.appending(component: "vietnamese-minimal-pairs", directoryHint: .isDirectory)
			.appending(component: dateFormatter.string(from: .now), directoryHint: .isDirectory)

		try FileManager.default.createDirectory(at: exportDirectory, withIntermediateDirectories: true)
		try Data(csvContent.utf8)
			.write(to: exportDirectory.appending(path: "notes").appendingPathExtension("csv"))
	}
	mutating func run() async throws {
		let minimalPairComponents = try String(contentsOf: self.minimalPairComponentsFile)
			.trimmingCharacters(in: .whitespacesAndNewlines)
			.split(separator: "\n")
			.map { line in
				let trimmedLine = line
					.trimmingCharacters(in: .whitespacesAndNewlines)
					.split(separator: "|")
				return MinimalPairComponent(
					distinctiveFeature: trimmedLine[0].trimmingCharacters(in: .whitespaces),
					word: trimmedLine[1].trimmingCharacters(in: .whitespaces)
				)
			}
			.sorted { $0.word < $1.word }

		try await downloadMissingAudioFiles(
			minimalPairComponents: minimalPairComponents
		)
		try exportCSVFile(minimalPairComponents: minimalPairComponents)
	}
}

