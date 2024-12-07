FROM ubuntu:22.04 as builder
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y libssl-dev build-essential curl
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /usr/src/app

COPY rust_server/Cargo.toml ./
COPY rust_server/src ./src
COPY rust_server/sample_solution.csv ./sample_solution.csv

RUN cargo build --release

FROM ubuntu:22.04
WORKDIR /app

COPY --from=builder /usr/src/app/target/release/rust_server .
COPY --from=builder /usr/src/app/sample_solution.csv .

EXPOSE 8000

CMD ["./rust_server"]
